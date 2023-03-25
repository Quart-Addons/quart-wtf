"""
quart_wtf.typing

Provides types for Quart WTF.
"""
import typing as t

from quart import Blueprint

from werkzeug.datastructures import (
    CombinedMultiDict,
    ImmutableDict,
    MultiDict
)

FormData = t.Union[CombinedMultiDict, ImmutableDict, MultiDict, None]

ViewsType = t.Union[Blueprint, t.Callable[..., t.Any], str]
