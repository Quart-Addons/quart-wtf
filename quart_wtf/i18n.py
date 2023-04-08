"""
quart_wtf.i18n

Translation support for Quart WTF.
"""
from numbers import Number

from quart import request
from quart_babel import Domain
from quart_babel.utils import get_state

def _get_translations() -> Domain | None:
    """
    Returns the correct Babel domain object
    for WTForms.
    """
    state = get_state(silent=True)

    if not state:
        return None

    if not request:
        return None

    translations = getattr(request, "wtforms_translations", None)

    if translations is None:
        translations = Domain(domain="wtforms")
        request.wtforms_translations = translations

    return translations

class Translations:
    """
    I18N translations using `quart_babel`.
    """
    def gettext(self, string: str) -> str:
        """
        Translates a string with the current
        locale from `quart_babel`.
        """
        domain = _get_translations()
        return string if domain is None else domain.gettext(string)

    def ngettext(self, singular: str, plural: str, num: Number) -> str:
        """
        Translates a string with the current locale and passes in the
        given keyword arguments as mapping to a string formatting string.
        The `num` parameter is used to dispatch between singular and various
        plural forms of the message.  It is available in the format string
        as ``%(num)d`` or ``%(num)s``.
        """
        domain = _get_translations()

        if domain is None:
            return singular if num == 1 else plural

        return domain.ngettext(singular, plural, num)

translations = Translations()
