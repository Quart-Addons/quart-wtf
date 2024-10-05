"""
quart_wtf.i18n
"""
from __future__ import annotations
from typing import Optional

from babel import support
from quart import current_app, request
from quart_babel import get_locale
from wtforms.i18n import messages_path


def _get_translations() -> Optional[support.NullTranslations]:
    """
    Returns the correct gettext translations.
    Copy from flask-babel with some modifications.
    """
    if not request:
        return None

    # babel should be in extension for get_locale
    if "babel" not in current_app.extensions:
        return None

    # pylint: disable=W0621
    translations = getattr(request, "wtforms_translations", None)

    if translations is None:
        translations = support.Translations.load(
            messages_path(), [get_locale()], domain="wtforms"
        )
        request.wtforms_translations = translations   # type: ignore

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
