"""
quart_wtf.utls

Utilities for Quart-WTF.
"""
from quart import request
from werkzeug.datastructures import MultiDict, CombinedMultiDict, ImmutableMultiDict

SUBMIT_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

def _is_submitted() -> bool:
    """
    Consider the form submitted if there is an active request and
    the method is ``POST``, ``PUT``, ``PATCH``, or ``DELETE``.
    """
    return bool(request) and request.method in SUBMIT_METHODS

async def _get_formdata() -> CombinedMultiDict | MultiDict | ImmutableMultiDict | None:
    """
    Return formdata from request. Handles multi-dict and json content types.
    Returns:
      formdata (ImmutableMultiDict): The form/json data from the request.
    """
    if await request.files:
        return CombinedMultiDict((await request.files, await request.form))
    elif await request.form:
        return await request.form
    elif request.is_json:
        return ImmutableMultiDict(await request.get_json())

    return None
