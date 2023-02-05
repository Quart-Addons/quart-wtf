"""
quart_wtf.typing

Provides types for Quart WTF.
"""
import os
import typing as t
from numbers import Number

from babel import support
from quart import Quart, Blueprint

from werkzeug.datastructures import (
    CombinedMultiDict,
    ImmutableDict,
    MultiDict
)

FormData = t.Union[CombinedMultiDict, ImmutableDict, MultiDict, None]

ViewsType = t.Union[Blueprint, t.Callable[..., t.Any], str]

_Translations = t.Union[support.Translations, support.NullTranslations]

class LazyString:
    def __init__(self, func: callable, *args, **kwargs):
        ...

    def __getattr__(self, attr):
        ...

    def __repr__(self):
        ...

    def __str__(self):
        ...

    def __len__(self):
        ...

    def __getitem__(self, key):
        ...

    def __iter__(self):
        ...

    def __contains__(self, item):
        ...

    def __add__(self, other):
        ...

    def __radd__(self, other):
        ...

    def __mul__(self, other):
        ...

    def __rmul__(self, other):
        ...

    def __lt__(self, other):
        ...

    def __le__(self, other):
        ...

    def __eq__(self, other):
        ...

    def __ne__(self, other):
        ...

    def __gt__(self, other):
        ...

    def __ge__(self, other):
        ...

    def __html__(self):
        ...

    def __hash__(self):
        ...

    def __mod__(self, other):
        ...

    def __rmod__(self, other):
        ...

class Domain:
    as_default: None
    translations_cache: dict
    translations: _Translations

    def __init__(
        self,
        dirname: str | os.PathLike[str] | None = None,
        domain: str = 'messages'
        ) -> None:
        ...

    def get_translations_path(self, app: Quart) -> str | os.PathLike[str]:
        ...

    def gettext(self, string: str, **variables) -> str:
        ...

    def ngettext(self, singular: str, plural: str, num: Number, **variables) -> str:
        ...

    def pgettext(self, context: str, string: str, **variables) -> str:
        ...

    def npgettext(
        self,
        context: str,
        singular: str,
        plural: str,
        num: Number,
        **variables
    ) -> str:
        ...

    def lazy_gettext(self, string: str, **variables) -> LazyString:
        ...

    def lazy_ngettext(
        self, singular: str, plural: str, num: Number, **variables
    ) -> LazyString:
        ...

    def lazy_pgettext(
        self, context: str, string: str, **variables
    ) -> LazyString:
        ...

class Translations:
    domain: Domain | None

    def _get_domain(self) -> Domain | None:
        ...

    def gettext(self, string: str) -> str:
        ...

    def ngettext(self, singular: str, plural: str, num: Number) -> str:
        ...
