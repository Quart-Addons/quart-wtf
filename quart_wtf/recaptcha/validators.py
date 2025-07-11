"""
quart_wtf.recaptcha.validators
"""
import json
from urllib import request as http
from urllib.parse import urlencode
from typing import Any

from quart import Quart, current_app, g
from quart import request
from wtforms import ValidationError
from werkzeug.local import LocalProxy


RECAPTCHA_VERIFY_SERVER_DEFAULT = \
    "https://www.google.com/recaptcha/api/siteverify"

RECAPTCHA_ERROR_CODES = {
    "missing-input-secret": "The secret parameter is missing.",
    "invalid-input-secret": "The secret parameter is invalid or malformed.",
    "missing-input-response": "The response parameter is missing.",
    "invalid-input-response": "The response parameter is invalid or malformed."
}


class Recaptcha:
    """
    Validates a ReCaptcha field.
    """
    def __init__(self, message: str | None = None) -> None:
        if message is None:
            message = RECAPTCHA_ERROR_CODES["invalid-input-response"]
        self.message = message

    def __call__(self, form: Any, field: Any) -> bool:
        if current_app.testing:
            return True

        response = getattr(g, "recaptcha", None)

        if not response:
            raise ValidationError(field.gettext(self.message))

        remote_ip = request.remote_addr
        valid = self._validate_recaptcha(response, remote_ip)

        if not valid:
            field.recaptcha_error = "incorrect_captcha-sol"
            raise ValidationError(field.gettext(self.message))
        else:
            return valid

    def _validate_recaptcha(
            self, response: Any, remote_addr: str | None
    ) -> bool:
        """
        Validate ReCaptcha
        """
        private_key = current_app.config.get("RECAPTCHA_PRIVATE_KEY")

        if not private_key:
            raise RuntimeError("No RECAPTCHA_PRIVATE_KEY in config")

        verify_server = current_app.config.get("RECAPTCHA_VERIFY_SERVER")
        if not verify_server:
            verify_server = RECAPTCHA_VERIFY_SERVER_DEFAULT

        data = urlencode(
            {
                "secret": private_key,
                "response": response,
                "remoteip": remote_addr
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


def recaptcha_before_request(app: Quart) -> None:
    """
    Registers the before request function to
    be used with the recaptcha field.

    This is a helper function that needs to be
    registered with `quart.Quart` when using
    the provided `qtf_forms.recaptcha.RecaptchaField`.

    It allows `quart.request.get_json` and
    `quart.request.form` to be called, since they
    can't be called within the field 
    """
    @app.before_request
    async def _recaptcha_response() -> None:
        if request.is_json:
            data = await request.get_json()
        else:
            data = await request.form
        response = data.get("g-recaptcha-response", "")
