"""
quart_wtf.csrf

CSRF helpers.
"""
import hashlib
import hmac
import logging
import os
import typing as t
from urllib.parse import urlparse

from itsdangerous import BadData, SignatureExpired, URLSafeTimedSerializer
from quart import Blueprint, current_app, g, Quart, request, session
from werkzeug.exceptions import BadRequest
from wtforms import ValidationError
from wtforms.csrf.core import CSRF

from .const import (FIELD_NAME_REQUIRED, REFERRER_HEADER, REFERRER_HOST,
                   SECRET_KEY_REQUIRED, SESSION_TOKEN_MISSING, TOKEN_INVALID,
                   TOKEN_EXPIRED, TOKEN_MISSING, TOKEN_NO_MATCH, VALIDATION_FAILED)

__all__ = ("generate_csrf", "validate_csrf", "CSRFProtect")
logger = logging.getLogger(__name__)

def _get_config(
    value: t.Optional[t.Any],
    config_name:str,
    default: t.Optional[t.Any],
    required: bool=True,
    message: str="CSRF is not configured.CSRF is not configured."):
    """
    Find config value based on provided value, Quart config, and default
    value.
    :param value: already provided config value
    :param config_name: Quart ``config`` key
    :param default: default value if not provided or configured
    :param required: whether the value must not be ``None``
    :param message: error message if required config is not found
    :raises KeyError: if required config is not found
    """
    if value is None:
        value = current_app.config.get(config_name, default)

    if required and value is None:
        raise RuntimeError(message)

    return value

def generate_csrf(secret_key=None, token_key=None):
    """
    Generate a CSRF token. The token is cached for a request, so multiple
    calls to this function will generate the same token.
    During testing, it might be useful to access the signed token in
    ``g.csrf_token`` and the raw token in ``session['csrf_token']``.
    :param secret_key: Used to securely sign the token. Default is
        ``WTF_CSRF_SECRET_KEY`` or ``SECRET_KEY``.
    :param token_key: Key where token is stored in session for comparison.
        Default is ``WTF_CSRF_FIELD_NAME`` or ``'csrf_token'``.
    """
    secret_key = _get_config(
        secret_key,
        "WTF_CSRF_SECRET_KEY",
        current_app.secret_key,
        message=SECRET_KEY_REQUIRED
    )

    field_name = _get_config(
        token_key,
        "WTF_CSRF_FIELD_NAME",
        "csrf_token",
        message=FIELD_NAME_REQUIRED
    )

    if field_name not in g:
        serial = URLSafeTimedSerializer(secret_key, salt="wtf-csrf-token")

        if field_name not in session:
            session[field_name] = hashlib.sha1(os.urandom(64)).hexdigest()

        try:
            token = serial.dumps(session[field_name])
        except TypeError:
            session[field_name] = hashlib.sha1(os.urandom(64)).hexdigest()
            token = serial.dumps(session[field_name])

        setattr(g, field_name, token)

    return g.get(field_name)

def validate_csrf(
    data,
    secret_key: t.Optional[t.Any]=None,
    time_limit: t.Optional[int]=None,
    token_key: t.Optional[str]=None
) -> None:
    """"
    Check if the given data is a valid CSRF token. This compares the given
    signed token to the one stored in the session.
    :param data: The signed CSRF token to be checked.
    :param secret_key: Used to securely sign the token. Default is
        ``WTF_CSRF_SECRET_KEY`` or ``SECRET_KEY``.
    :param time_limit: Number of seconds that the token is valid. Default is
        ``WTF_CSRF_TIME_LIMIT`` or 3600 seconds (60 minutes).
    :param token_key: Key where token is stored in session for comparison.
        Default is ``WTF_CSRF_FIELD_NAME`` or ``'csrf_token'``.
    :raises ValidationError: Contains the reason that validation failed.
        Raises ``ValidationError`` with a specific error message rather than
        returning ``True`` or ``False``.
    """
    secret_key = _get_config(
        secret_key,
        "WTF_CSRF_SECRET_KEY",
        current_app.secret_key,
        message=SECRET_KEY_REQUIRED
    )

    field_name = _get_config(
        token_key,
        "WTF_CSRF_FIELD_NAME",
        "csrf_token",
        message=FIELD_NAME_REQUIRED
    )

    time_limit = _get_config(
        time_limit,
        "WTF_CSRF_TIME_LIMIT",
        3600,
        required=False
    )

    if not data:
        raise ValidationError(TOKEN_MISSING)

    if field_name not in session:
        raise ValidationError(SESSION_TOKEN_MISSING)

    serial = URLSafeTimedSerializer(secret_key, salt="wtf-csrf-token")

    try:
        token = serial.loads(data, max_age=time_limit)
    except SignatureExpired as error:
        raise ValidationError(TOKEN_EXPIRED) from error
    except BadData as error:
        raise ValidationError(TOKEN_INVALID) from error

    if not hmac.compare_digest(session[field_name], token):
        raise ValidationError(TOKEN_NO_MATCH)

def same_origin(current_uri: str, compare_uri: str) -> bool:
    """
    Determines if the request is from the same origin.
    """
    current = urlparse(current_uri)
    compare = urlparse(compare_uri)

    return (
        current.scheme == compare.scheme
        and current.hostname == compare.hostname
        and current.port == compare.port
    )

class _QuartFormCSRF(CSRF):
    def setup_form(self, form):
        self.meta = form.meta
        return super(_QuartFormCSRF, self).setup_form(form)

    def generate_csrf_token(self, csrf_token_field):
        token = generate_csrf(
            secret_key=self.meta.csrf_secret,
            token_key=self.meta.csrf_field_name
        )
        return token

    def validate_csrf_token(self, form, field):
        if g.get("csrf_valid", False):
            # already validated by CSRFProtect.
            return

        try:
            validate_csrf(
                field.data,
                self.meta.csrf_secret,
                self.meta.csrf_time_limit,
                self.meta.csrf_field_name
            )
        except ValidationError as error:
            logger.info(error.args[0])
            raise

class CSRFProtect:
    """
    Enable CSRF protection globally for a Quart app.
    ::
        app = Quart(__name__)
        csrf = CSRFProtect(app)
    Checks the ``csrf_token`` field sent with forms, or the ``X-CSRFToken``
    header sent with JavaScript requests. Render the token in templates using
    ``{{ csrf_token() }}``.
    See the :ref:`csrf` documentation.
    """
    def __init__(self, app: t.Optional[Quart]=None) -> None:
        """
        Initialize the `CSRFProtect` class.
        """
        self._exempt_views = set()
        self._exempt_blueprints = set()

        if app:
            self.init_app(app)

    def init_app(self, app: Quart) -> None:
        """
        Initialize the `CSRFProtect` class with
        the `Quart` app.
        """
        app.extensions["csrf"] = self

        app.config.setdefault("WTF_CSRF_ENABLED", True)
        app.config.setdefault("WTF_CSRF_CHECK_DEFAULT", True)
        app.config["WTF_CSRF_METHODS"] = set(
            app.config.get("WTF_CSRF_METHODS", ["POST", "PUT", "PATCH", "DELETE"])
        )
        app.config.setdefault("WTF_CSRF_FIELD_NAME", "csrf_token")
        app.config.setdefault("WTF_CSRF_HEADERS", ["X-CSRFToken", "X-CSRF-Token"])
        app.config.setdefault("WTF_CSRF_TIME_LIMIT", 3600)
        app.config.setdefault("WTF_CSRF_SSL_STRICT", True)

        app.jinja_env.globals["csrf_token"] = generate_csrf
        app.context_processor(self.csrf_context_processor())

        @app.before_request
        async def csrf_protect():
            if not app.config["WTF_CSRF_ENABLED"]:
                return

            if not app.config["WTF_CSRF_CHECK_DEFAULT"]:
                return

            if request.method not in app.config["WTF_CSRF_METHODS"]:
                return

            if not request.endpoint:
                return

            if request.blueprint in self._exempt_blueprints:
                return

            view = app.view_functions.get(request.endpoint)
            dest = f"{view.__module__}.{view.__name__}"

            if dest in self._exempt_views:
                return

            await self.protect()

    async def csrf_context_processor(self):
        """
        App Context Processor for CSRF.
        """
        return {"csrf_token": generate_csrf}

    async def _get_csrf_token(self) -> t.Optional[t.Any]:
        """
        Gets the CSRF token.
        """
        # find the token in the form data.
        field_name = current_app.config["WTF_CSRF_FIELD_NAME"]
        form = await request.form
        base_token = form.get(field_name)

        if base_token:
            return base_token

        # if the form has a prefix, the name will be
        # {prefix}-csrf_token
        for key in form:
            if key.endswith(field_name):
                csrf_token = form[key]

                if csrf_token:
                    return csrf_token

        # find the token in the request headers
        for header_name in current_app.config["WTF_CSRF_HEADERS"]:
            csrf_token = request.headers[header_name]

            if csrf_token:
                return csrf_token

        return None

    async def protect(self) -> None:
        """
        Provides the CSRF protection for the app.
        """
        if request.method not in current_app.config["WTF_CSRF_METHODS"]:
            return

        csrf_token = await self._get_csrf_token()

        try:
            validate_csrf(csrf_token)
        except ValidationError as error:
            logger.info(error.args[0])
            self._error_response(error.args[0])

        if request.is_secure and current_app.config["WTF_CSRF_SSL_STRICT"]:
            if not request.referrer:
                self._error_response(REFERRER_HEADER)

            good_referrer = f"https://{request.host}/"

            if not same_origin(request.referrer, good_referrer):
                self._error_response(REFERRER_HOST)

        g.csrf_valid = True

    def exempt(self, view):
        """
        Mark a view or blueprint to be excluded from CSRF protection.
        ::
            @app.route('/some-view', methods=['POST'])
            @csrf.exempt
            async def some_view():
                ...
        ::
            bp = Blueprint(...)
            csrf.exempt(bp)
        """
        if isinstance(view, Blueprint):
            self._exempt_blueprints.add(view.name)
            return view

        if isinstance(view, str):
            view_location = view
        else:
            view_location = ".".join((view.__module__, view.__name__))

        self._exempt_views.add(view_location)
        return view

    def _error_response(self, reason: str) -> None:
        """
        Raises as a `CSRFError` with a specific reason.
        """
        raise CSRFError(reason)

class CSRFError(BadRequest):
    """Raise if the client sends invalid CSRF data with the request.
    Generates a 400 Bad Request response with the failure reason by default.
    Customize the response by registering a handler with
    :meth:`quart.Quart.errorhandler`.
    """

    description = VALIDATION_FAILED
