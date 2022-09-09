"""
quart_wtf.meta

Defines the WTF meta and CSRF class for Quart-WTF.
"""
from quart import current_app, g, session
from werkzeug.utils import cached_property
from wtforms import ValidationError
from wtforms.csrf.core import CSRF
from wtforms.meta import DefaultMeta

from .utils import logger, generate_csrf, validate_csrf

__all__ = ["QuartFormMeta"]

class _QuartFormCSRF(CSRF):
    def setup_form(self, form):
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
                field.data,
                self.meta.csrf_secret,
                self.meta.csrf_time_limit,
                self.meta.csrf_field_name
            )
        except ValidationError as error:
            logger.info(error.args[0])
            raise

class QuartFormMeta(DefaultMeta):
    """
    Meta class for Quart specific subclass of WTForms.
    """
    csrf_class = _QuartFormCSRF
    csrf_context = session

    @cached_property
    def csrf(self) -> bool:
        """
        Determines if CSRF is enabled.
        """
        return current_app.config.get("WTF_CSRF_ENABLED", True)

    @cached_property
    def csrf_secret(self):
        """
        CSRF secret key.
        """
        return current_app.config.get("WTF_CSRF_SECRET_KEY", current_app.secret_key)

    @cached_property
    def csrf_field_name(self) -> str:
        """
        CSRF field name.
        """
        return current_app.config.get('WTF_CSRF_FIELD_NAME', "csrf_token")

    @cached_property
    def csrf_time_limit(self):
        """
        CSRF time limit.
        """
        return current_app.config.get("WTF_CSRF_TIME_LIMIT", 3600)
