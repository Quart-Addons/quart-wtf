"""
quart_wtf.i18n

Translation support for Quart WTF.
"""
from numbers import Number

from quart_babel import Domain
from quart_babel.utils import get_state

__all__ = ("Translations", "translations")

class Translations:
    """
    Provides translation support to `quart_wtf` using
    `quart_babel`.
    """
    _domain: Domain | None = None

    @property
    def domain(self) -> Domain | None:
        """
        Returns the domain to use. Defaults
        to ``None``.
        """
        return self._domain

    @domain.setter
    def domain(self, value: Domain) -> None:
        self._domain = value

    def _get_domain(self) -> Domain | None:
        """
        Get the `quart_babel.domain` to use for
        translations.

        This function will first determine the babel
        state by calling `quart_babel.utils.get_state`
        function in silent mode.

        If the state is ``None`` (Babel is not registered
        with the app) it will return ``None``. Otherwise
        it will determine if `Translations.domain` is ``None``
        and will call the default domain from babel. Else it
        will use the custom domain provided.
        """
        state = get_state(silent=True)

        if not state:
            return None

        if self.domain is None:
            return state.domain

        return self.domain

    def gettext(self, string: str) -> str:
        """
        Translates a string with the current
        locale from `quart_babel`.

        Arguments:
            string: The string to translate.
        """
        trans = self._get_domain()
        return string if trans is None else trans.gettext(string)

    def ngettext(self, singular: str, plural: str, num: Number) -> str:
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
        trans = self._get_domain()

        if trans is None:
            return singular if num == 1 else plural

        return trans.ngettext(singular, plural, num)

translations = Translations()
