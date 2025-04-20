"""
quart_wtf.typing
"""
from typing import Any, Awaitable, Callable, Union

from quart import Blueprint

from werkzeug.datastructures import (
    CombinedMultiDict,
    MultiDict
)

FormData = Union[CombinedMultiDict, MultiDict]

ViewsType = Union[str, Blueprint, Callable[..., Awaitable[Any]]]
