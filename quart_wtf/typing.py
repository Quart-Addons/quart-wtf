"""
quart_wtf.typing
"""
from typing import Any, Awaitable, Callable, Union
from gettext import GNUTranslations
from numbers import Number

from quart import Blueprint

from werkzeug.datastructures import (
    CombinedMultiDict,
    ImmutableDict,
    MultiDict
)

FormData = Union[CombinedMultiDict, ImmutableDict, MultiDict]

ViewsType = Union[str, Blueprint, Callable[..., Awaitable[Any]]]

class Translations:
    """
    I18N translations using `quart_babel`.
    """
    def gettext(self, string: str) -> str:
        ...

    def ngettext(self, singular: str, plural: str, num: Number) -> str:
        ...

TranslationsTypes = Union[GNUTranslations, Translations, None]
