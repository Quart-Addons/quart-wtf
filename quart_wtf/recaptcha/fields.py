"""
quart_forms.recaptch.fields
"""
from wtforms.fields import Field

from .widgets import RecaptchaWidget
from .validators import async_validate_Recaptcha

__all__ = ["RecaptchaField"]


class RecaptchaField(Field):
    """
    Repcaptcha Field for `quart_forms`.
    """
    widget = RecaptchaWidget

    # error message if recaptcha validation fails
    recaptcha_error = None

    def __init__(self, label="", validators=None, **kwargs):
        validators = validators or [async_validate_Recaptcha()]
        super().__init__(label, validators, **kwargs)
