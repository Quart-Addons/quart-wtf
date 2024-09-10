"""
quart_wtf.meta
"""
from typing import Any

from quart import current_app, g, session
from werkzeug.utils import cached_property
from wtforms import ValidationError  # type: ignore
from wtforms.csrf.core import CSRF  # type: ignore
from wtforms.meta import DefaultMeta  # type: ignore

from .const import (
    DEFAULT_ENABLED,
    DEFAULT_CSRF_FIELD_NAME,
    DEFAULT_CSRF_TIME_LIMIT
    )

from .utils import logger, generate_csrf, validate_csrf

try:
    from .i18n import translations
except ImportError:
    translations = None  # quart_babel not installed.


class _QuartFormCSRF(CSRF):  # type: ignore
    meta = None

    def setup_form(self, form):  # type: ignore
        """
        Setup the form for CSRF.
        """
        self.meta = form.meta
        return super().setup_form(form)

    def generate_csrf_token(self, csrf_token_field):  # type: ignore
        return generate_csrf(
            secret_key=self.meta.csrf_secret,
            token_key=self.meta.csrf_field_name
        )

    def validate_csrf_token(self, form, field):  # type: ignore
        if g.get("csrf_valid", False):
            # Already protected by CSRF Protect.
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


class QuartFormMeta(DefaultMeta):  # type: ignore
    """
    Quart specific meta class for WTForms.
    """
    csrf_class = _QuartFormCSRF
    csrf_context = session  # not used, provided for custom CSRF class.

    @cached_property
    def csrf(self) -> bool:
        """
        CSRF Enabled.
        """
        return current_app.config.get("WTF_CSRF_ENABLED", DEFAULT_ENABLED)

    @cached_property
    def csrf_secret(self) -> Any:
        """
        CSRF secret key.
        """
        return current_app.config.get(
            "WTF_CSRF_SECRET_KEY", current_app.secret_key
            )

    @cached_property
    def csrf_field_name(self) -> str:
        """
        CSRF field name.
        """
        return current_app.config.get(
            "WTF_CSRF_FIELD_NAME", DEFAULT_CSRF_FIELD_NAME
            )

    @cached_property
    def csrf_time_limit(self) -> int:
        """
        CSRF time limit.
        """
        return current_app.config.get(
            "WTF_CSRF_TIME_LIMIT", DEFAULT_CSRF_TIME_LIMIT
            )

    def get_translations(self, form):  # type: ignore
        """
        Gets translations for the form. If the configuration
        variable 'WTF_I18N_ENABLED' is ``False`` will use
        `DefaultMeta.get_translations`.
        """
        if not current_app.config.get("WTF_I18N_ENABLED", True):
            return super().get_translations(form)
        return translations
