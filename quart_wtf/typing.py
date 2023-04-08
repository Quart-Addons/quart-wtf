"""
quart_wtf.typing
"""
import typing as t

from quart import Blueprint

from werkzeug.datastructures import (
    CombinedMultiDict,
    ImmutableDict,
    MultiDict
)

FormData = t.Union[CombinedMultiDict, ImmutableDict, MultiDict]

ViewsType = t.Union[str, Blueprint, t.Callable[..., t.Awaitable[t.Any]]]
