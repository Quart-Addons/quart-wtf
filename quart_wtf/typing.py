"""
quart_wtf.typing
"""
from typing import Any, Awaitable, Callable, TypeVar, Union

from quart import Blueprint

from werkzeug.datastructures import (
    CombinedMultiDict,
    ImmutableDict,
    MultiDict
)

FormData = Union[CombinedMultiDict, ImmutableDict, MultiDict]

ViewsType = TypeVar("ViewsType", str, Blueprint, Callable[..., Awaitable[Any]])
