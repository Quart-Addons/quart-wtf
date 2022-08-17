"""
quart_wtf.meta

Defines the WTF meta class for Quart-WTF.
"""
from quart import current_app, session
from wtforms.meta import DefaultMeta
from werkzeug.utils import cached_property

from .csrf.form import _QuartFormCSRF

class QuartFormMeta(DefaultMeta):
    """
    Meta class for Quart specific subclass of WTForms.
    """
    csrf_class = _QuartFormCSRF
    csrf_context = session

    @property
    def csrf(self) -> bool:
        """
        Determines if CSRF is enabled.
        """
        return current_app.config.get("WTF_CSRF_ENABLED", True)

    @property
    def csrf_secret(self):
        """
        CSRF secret key.
        """
        return current_app.config.get("WTF_CSRF_SECRET_KEY", current_app.secret_key)

    @property
    def csrf_field_name(self) -> str:
        """
        CSRF field name.
        """
        return current_app.config.get('WTF_CSRF_FIELD_NAME', "csrf_token")

    @property
    def csrf_time_limit(self):
        """
        CSRF time limit.
        """
        return current_app.config.get("WTF_CSRF_TIME_LIMIT", 3600)
