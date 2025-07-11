"""
quart.wtf.recaptcha.widgets
"""
from urllib.parse import urlencode
from typing import Any

from quart import current_app
from markupsafe import Markup


RECAPTCHA_SCRIPT_DEFAULT = "https://www.google.com/recaptcha/api.js"
RECAPTCHA_DIV_CLASS_DEFAULT = "g-recaptcha"
RECAPTCHA_TEMPLATE = """
<script src='%s' async defer></script>
<div class="%s" %s></div>
"""

__all__ = ["RecaptchaWidget"]


class RecaptchaWidget:
    """
    Recaptcha Widget for `quart_forms`.
    """
    def recaptcha_html(self, public_key: str) -> Markup:
        """
        Returns the html
        """
        html = current_app.config.get("RECAPTCHA_HTML")
        if html:
            return Markup(html)
        params = current_app.config.get("RECAPTCHA_PARAMETERS")
        script = current_app.config.get("RECAPTCHA_SCRIPT")
        if not script:
            script = RECAPTCHA_SCRIPT_DEFAULT
        if params:
            script += "?" + urlencode(params)
        attrs = current_app.config.get("RECAPTCHA_DATA_ATTRS", {})
        attrs["sitekey"] = public_key
        snippet = " ".join(f'data-{k}="{attrs[k]}"' for k in attrs)
        div_class = current_app.config.get("RECAPTCHA_DIV_CLASS")
        if not div_class:
            div_class = RECAPTCHA_DIV_CLASS_DEFAULT
        return Markup(RECAPTCHA_TEMPLATE % (script, div_class, snippet))

    def __call__(
            self, field: Any, error: Any | None = None, **kwargs: Any
    ) -> Markup:
        """Returns the recaptcha input HTML."""

        try:
            public_key = current_app.config["RECAPTCHA_PUBLIC_KEY"]
        except KeyError:
            raise RuntimeError("RECAPTCHA_PUBLIC_KEY config not set") from None

        return self.recaptcha_html(public_key)
