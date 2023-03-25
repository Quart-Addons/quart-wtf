"""
quart_wtf.i18n

Translation support for Quart WTF.
"""
from numbers import Number

from quart import request
from quart_babel import Domain
from quart_babel.utils import get_state

class Translations:
    """
    i18n translations using `Quart_Babel`.
    """
    domain: Domain | None = None

    def _get_translations(self) -> Domain | None:
        """
        Returns the correct translations object for the
        WTForms Babel domain.
        """
        state = get_state(silent=True)
        if not state:
            return None

        translations = getattr(request, "wtforms_translations", None)

        if translations is None:
            if self.domain is None:
                self.domain = Domain(domain="wtforms")
            translations = self.domain

        return translations

    def gettext(self, string: str):
        """
        Translates a string with the current
        locale from `quart_babel`.

        Arguments:
            string: The string to translate.
        """
        domain = self._get_translations()
        return string if domain is None else domain.gettext(string)

    def ngettext(self, singular: str, plural: str, num: Number):
        """
        Translates a string with the current locale and passes in the
        given keyword arguments as mapping to a string formatting string.
        The `num` parameter is used to dispatch between singular and various
        plural forms of the message.  It is available in the format string
        as ``%(num)d`` or ``%(num)s``.

        Arguments:
            singular: The singular string of the text.
            plural: the plural string of the text.
            num: The number parameter.
        """
        domain = self._get_translations()

        if domain is None:
            return singular if num == 1 else plural

        return domain.ngettext(singular, plural, num)

translations = Translations()
