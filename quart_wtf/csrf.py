"""
quart_wtf.csrf
"""
from __future__ import annotations
from typing import Any, List

from quart import (
    Quart,
    Blueprint,
    current_app,
    g,
    request
)

from werkzeug.exceptions import BadRequest
from wtforms import ValidationError  # type: ignore

from .const import (
    DEFAULT_ENABLED,
    DEFAULT_CHECK_DEFAULT,
    DEFAULT_CSRF_FIELD_NAME,
    DEFAULT_CSRF_HEADERS,
    DEFAULT_CSRF_TIME_LIMIT,
    DEFAULT_CSRF_SSL_STRICT,
    DEFAULT_SUBMIT_METHODS,
    REFERRER_HEADER,
    REFERRER_HOST,
    VALIDATION_FAILED
)

from .typing import ViewsType
from .utils import logger, generate_csrf, validate_csrf, same_orgin


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
    def __init__(self, app: Quart | None = None) -> None:
        """
        Initialize the `CSRFProtect` class.

        Arguments:
            app: The `Quart` application.
        """
        self._exempt_views: List = list()
        self._exempt_blueprints: List = list()

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Quart) -> None:
        """
        Initialize the `CSRFProtect` class with
        the `Quart` app.

        Arguments:
            app: The `Quart` application.
        """
        app.config.setdefault("WTF_CSRF_ENABLED", DEFAULT_ENABLED)
        app.config.setdefault("WTF_CSRF_CHECK_DEFAULT", DEFAULT_CHECK_DEFAULT)
        app.config.setdefault("WTF_CSRF_METHODS", DEFAULT_SUBMIT_METHODS)
        app.config.setdefault("WTF_CSRF_FIELD_NAME", DEFAULT_CSRF_FIELD_NAME)
        app.config.setdefault("WTF_CSRF_HEADERS", DEFAULT_CSRF_HEADERS)
        app.config.setdefault("WTF_CSRF_TIME_LIMIT", DEFAULT_CSRF_TIME_LIMIT)
        app.config.setdefault("WTF_CSRF_SSL_STRICT", DEFAULT_CSRF_SSL_STRICT)

        app.extensions["csrf"] = self

        app.jinja_env.globals["csrf_token"] = generate_csrf
        app.context_processor(lambda: {"crsf_token": generate_csrf})

        @app.before_request
        async def csrf_protect() -> None:
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

    async def _get_csrf_token(self) -> Any | None:
        """
        Get the CSRF token.
        """
        field_name = current_app.config["WTF_CSRF_FIELD_NAME"]
        form = await request.form
        base_token = form.get(field_name)

        if base_token:
            return base_token

        # if the form has a prefix, the name will be {prefix}-csrf_token
        for key in form:
            if key.endswith(field_name):
                csrf_token = form[key]

                if csrf_token:
                    return csrf_token

        # find the token in the request headers
        for header_name in current_app.config["WTF_CSRF_HEADERS"]:
            csrf_token = request.headers.get(header_name)

            if csrf_token:
                return csrf_token

        return None

    def _error_response(self, reason: str) -> None:
        """
        Raises as a `CSRFError` with a specific reason.
        """
        raise CSRFError(reason)

    async def protect(self) -> None:
        """
        Provides the CSRF protection for the app.
        """
        if request.method not in current_app.config["WTF_CSRF_METHODS"]:
            return

        try:
            validate_csrf(await self._get_csrf_token())
        except ValidationError as error:
            logger.info(error.args[0])
            self._error_response(error.args[0])

        if request.is_secure and current_app.config["WTF_CSRF_SSL_STRICT"]:
            if not request.referrer:
                self._error_response(REFERRER_HEADER)

            good_referrer = f"https://{request.host}"

            if not same_orgin(request.referrer, good_referrer):
                self._error_response(REFERRER_HOST)

        g.csrf_valid = True  # Mark this request as CSRF valid.

    def exempt(self, view: ViewsType) -> ViewsType:
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

        Argument:
            view: The view function or a `quart.Blueprint` instance.
        """
        if isinstance(view, Blueprint):
            self._exempt_blueprints.append(view.name)
            return view

        if isinstance(view, str):
            view_location = view
        else:
            view_location = ".".join((view.__module__, view.__name__))

        self._exempt_views.append(view_location)
        return view


class CSRFError(BadRequest):
    """
    Raise if the client sends invalid CSRF data with the request.
    Generates a 400 Bad Request response with the failure reason by default.
    Customize the response by registering a handler with
    :meth:`quart.Quart.errorhandler`.
    """
    description = VALIDATION_FAILED
