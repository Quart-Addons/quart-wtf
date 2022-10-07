"""
quart_wtf.meta

Defines the WTF meta and CSRF class for Quart-WTF.
"""
from typing import Any
from quart import current_app, g, session
from werkzeug.utils import cached_property
from wtforms import ValidationError
from wtforms.csrf.core import CSRF
from wtforms.meta import DefaultMeta

from .const import DEFAULT_ENABLED, DEFAULT_CSRF_FIELD_NAME, DEFAULT_CSRF_TIME_LIMIT
from .utils import logger, generate_csrf, validate_csrf

__all__ = ["QuartFormMeta"]

class _QuartFormCSRF(CSRF):
    meta = None

    def setup_form(self, form):
        """
        Setup the form for CSRF.
        """
        self.meta = form.meta

        return super().setup_form(form)

    def generate_csrf_token(self, csrf_token_field):

        return generate_csrf(
            secret_key=self.meta.csrf_secret,
            token_key=self.meta.csrf_field_name
        )

    def validate_csrf_token(self, form, field):

        if g.get("csrf_valid", False):
            # already validated by CSRFProtect.
            return

        try:
            validate_csrf(
                data=field.data,
                secret_key=self.meta.csrf_secret,
                time_limit=self.meta.csrf_time_limit,
                token_key=self.meta.csrf_field_name
            )
        except ValidationError as error:
            logger.info(error.args[0])
            raise

class QuartFormMeta(DefaultMeta):
    """
    Meta class for Quart specific subclass of WTForms.
    """
    csrf_class = _QuartFormCSRF
    csrf_context = session # not used, provided for custom CSRF class.

    @cached_property
    def csrf(self) -> bool:
        """
        Determines if CSRF is enabled.
        """
        return current_app.config.get("WTF_CSRF_ENABLED", DEFAULT_ENABLED)

    @cached_property
    def csrf_secret(self) -> Any:
        """
        CSRF secret key.
        """
        return current_app.config.get("WTF_CSRF_SECRET_KEY", current_app.secret_key)

    @cached_property
    def csrf_field_name(self) -> str:
        """
        CSRF field name.
        """
        return current_app.config.get('WTF_CSRF_FIELD_NAME', DEFAULT_CSRF_FIELD_NAME)

    @cached_property
    def csrf_time_limit(self) -> int:
        """
        CSRF time limit.
        """
        return current_app.config.get("WTF_CSRF_TIME_LIMIT", DEFAULT_CSRF_TIME_LIMIT)
