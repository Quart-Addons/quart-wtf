"""
quart_wtf.typing
"""
from typing import Any, Awaitable, Callable, Union

from quart import Blueprint

from werkzeug.datastructures import (
    CombinedMultiDict,
    ImmutableDict,
    MultiDict
)

FormData = Union[CombinedMultiDict, ImmutableDict, MultiDict]

ViewsType = Union[str, Blueprint, Callable[..., Awaitable[Any]]]
