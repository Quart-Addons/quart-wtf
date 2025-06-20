"""
quart_wtf.recaptcha.validators
"""
import json
from urllib import request as http
from urllib.parse import urlencode
from typing import Any

from quart import current_app, request
from wtforms import ValidationError


RECAPTCHA_VERIFY_SERVER_DEFAULT = \
    "https://www.google.com/recaptcha/api/siteverify"
RECAPTCHA_ERROR_CODES = {
    "missing-input-secret": "The secret parameter is missing.",
    "invalid-input-secret": "The secret parameter is invalid or malformed.",
    "missing-input-response": "The response parameter is missing.",
    "invalid-input-response": "The response parameter is invalid or malformed."
}


__all__ = ["recaptcha_validation"]


def _validate_recaptcha(response: Any, remote_addr: str) -> bool:
    """
    Performs the actual validation
    """
    try:
        private_key = current_app.config["RECAPTCHA_PRIVATE_KEY"]
    except KeyError:
        raise RuntimeError("No RECAPTCHA_PRIVATE_KEY config set") from None
    verify_server = current_app.config.get("RECAPTCHA_VERIFY_SERVER")
    if not verify_server:
        verify_server = RECAPTCHA_VERIFY_SERVER_DEFAULT
    data = urlencode(
        {
            "secret": private_key,
            "remoteip": remote_addr,
            "response": response
            }
    )
    http_response = http.urlopen(verify_server, data.encode("utf-8"))
    if http_response.code != 200:
        return False
    json_resp = json.loads(http_response.read())
    if json_resp["success"]:
        return True
    for error in json_resp.get("error-codes", []):
        if error in RECAPTCHA_ERROR_CODES:
            raise ValidationError(RECAPTCHA_ERROR_CODES[error])
    return False


async def recaptcha_validation(field: Any, message: str | None) -> None:
    """
    Validation of the recaptcha field. This function
    is async, since it uses the `quart.request`.

    The function needs to be used as inline form validator
    so that it will be awaited

    Example usage:

    .. code-block:: python
        from quart_wtforms import QuartForm
        from quart_wrforms.recaptcha import (
            RecaptchaField,
            recaptcha_validation
            )

        class Form(QuartForm):
            recaptcha = RepcaptchaField()

            async def async_validate_recaptcha(self, field) -> None:
                return await recaptcha_validation(field)

    Args:
        field: The recaptcha field, which will be passed by the form class.
        message: Custom error message. If one is not provided, the function
            will provide one.
    """
    if current_app.testing:
        return

    if message is None:
        message = RECAPTCHA_ERROR_CODES["missing-input-response"]

    if request.is_json:
        response = (await request.get_json()).get("g-recaptcha-response", "")
    else:
        response = (await request.form).get("g-recaptcha-response", "")

    remote_ip = request.remote_addr

    if not response:
        raise ValidationError(field.gettext(message))

    if not _validate_recaptcha(response, remote_ip):
        field.recpatcha_error = "incorrect-captcha_sol"
        raise ValidationError(field.gettext(message))
    return
