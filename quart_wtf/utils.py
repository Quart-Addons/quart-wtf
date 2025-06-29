"""
quart_wtf.utils
"""
import hashlib
import hmac
import logging
import os
import typing as t
from urllib.parse import urlparse

from itsdangerous import BadData, SignatureExpired, URLSafeTimedSerializer
from quart import current_app, g, session
from wtforms import ValidationError

from .const import (
    CSRF_NOT_CONFIGURED,
    FIELD_NAME_REQUIRED,
    SECRET_KEY_REQUIRED,
    SESSION_TOKEN_MISSING,
    TOKEN_EXPIRED,
    TOKEN_INVALID,
    TOKEN_MISSING,
    TOKEN_NO_MATCH
)


logger = logging.getLogger("Quart-WTF")


def _get_config(
    value: t.Any,
    config_name: str,
    default: t.Any | None = None,
    required: bool = True,
    message: str = CSRF_NOT_CONFIGURED
) -> t.Any:
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


def generate_csrf(
    secret_key: t.Any | None = None,
    token_key: t.Any | None = None
) -> t.Any:
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
    data: t.Any,
    secret_key: t.Any | None = None,
    time_limit: int | None = None,
    token_key: t.Any | None = None
) -> None:
    """
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


def same_orgin(current_uri: str, compare_uri: str) -> bool:
    """
    Determines if the request is from the same origin.

    :param current_uri: The current uri
    :param compare_uri: The uri to compare to the current uri.
    """
    current = urlparse(current_uri)
    compare = urlparse(compare_uri)

    return (
        current.scheme == compare.scheme
        and current.hostname == compare.hostname
        and current.port == compare.port
    )
