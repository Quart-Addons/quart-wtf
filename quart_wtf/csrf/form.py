"""
quart_wtf.csrf.form

The CSRF class for QuartForm.
"""
from quart import g
from wtforms import ValidationError
from wtforms.csrf.core import CSRF

from .utils import logger, generate_csrf, validate_csrf

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
