"""
quart_wtf.i18n
"""
from babel import support
from quart import request
from quart_babel import get_locale  # type: ignore
from quart_babel.utils import get_state  # type: ignore
from wtforms.i18n import messages_path  # type: ignore


def _get_translations() -> support.NullTranslations | None:
    if not request:
        return None

    if not get_state(silent=True):
        # quart-babel not configured.
        return None

    support_translations = getattr(request, "wtforms_translations", None)

    if support_translations is None:
        support_translations = support.Translations.load(
            messages_path(), [get_locale()], domain="wtforms"
        )
        request.wtforms_translations = support_translations  # type: ignore

    return support_translations


class Translations:
    """
    I18N translations using `quart_babel`.
    """
    def gettext(self, string: str) -> str:
        """
        Translates a string with the current
        locale from `quart_babel`.
        """
        trans = _get_translations()
        return string if trans is None else trans.ugettext(string)

    def ngettext(self, singular: str, plural: str, num: int) -> str:
        """
        Translates a string with the current locale and passes in the
        given keyword arguments as mapping to a string formatting string.
        The `num` parameter is used to dispatch between singular and various
        plural forms of the message.  It is available in the format string
        as ``%(num)d`` or ``%(num)s``.
        """
        trans = _get_translations()

        if trans is None:
            return singular if num == 1 else plural

        return trans.ungettext(singular, plural, num)


translations = Translations()
