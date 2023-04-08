"""
quart_wtf.typing
"""
import typing as t

from werkzeug.datastructures import (
    CombinedMultiDict,
    ImmutableDict,
    MultiDict
)

FormData = t.Union[CombinedMultiDict, ImmutableDict, MultiDict]
