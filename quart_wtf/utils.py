"""
quart_wtf.utils

Utilities for `quart_wtf`.
"""
from typing import Optional, Union
from quart import request
from werkzeug.datastructures import MultiDict, CombinedMultiDict, ImmutableDict

SUBMIT_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

def _is_submitted() -> bool:
    """
    Consider the form submitted if there is an active request and
    the method is ``POST``, ``PUT``, ``PATCH``, or ``DELETE``.
    """
    return bool(request) and request.method in SUBMIT_METHODS

async def _get_formdata() -> Optional[Union[MultiDict, CombinedMultiDict, ImmutableDict]]:
    """
    Return formdata from request. Handles multi-dict and json content types.
    """
    files = await request.files
    form = await request.form

    if files:
        return CombinedMultiDict((files, form))
    elif form:
        return form
    elif request.is_json():
        return ImmutableDict(await request.get_json())

    return None
