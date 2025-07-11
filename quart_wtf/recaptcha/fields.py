"""
quart_forms.recaptcha.fields
"""
from typing import Any, List

from wtforms.fields import Field

from .validators import Recaptcha
from .widgets import RecaptchaWidget


__all__ = ["RecaptchaField"]


class RecaptchaField(Field):
    """
    Recaptcha Field for `quart_forms`.
    """
    widget = RecaptchaWidget()

    # error message if recaptcha validation fails
    recaptcha_error = None

    def __init__(
            self,
            label: str = "",
            validators: List[Any] | None = None,
            **kwargs: Any
    ) -> None:
        validators = validators or [Recaptcha()]
        super().__init__(label, validators, **kwargs)
