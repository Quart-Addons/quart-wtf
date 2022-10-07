"""
Quart-WTF Form
"""
from __future__ import annotations
import asyncio
from typing import Any, Coroutine, Dict, Optional, Union
from markupsafe import Markup
from wtforms import Field, Form, ValidationError
from wtforms.widgets import HiddenInput
from werkzeug.datastructures import MultiDict, CombinedMultiDict, ImmutableMultiDict

from .meta import QuartFormMeta
from .utils import _is_submitted, _get_formdata

_Auto = object()

class QuartForm(Form):
    """
    Quart specific subclass of WTForms :class:`~wtforms.form.Form`.
    To populate from submitted formdata use the ```.from_submit()``` class
    method to initialize the instance.
    """
    Meta = QuartFormMeta

    def __init__(
        self,
        formdata: Optional[Union[MultiDict, CombinedMultiDict, ImmutableMultiDict]]=None,
        obj: Optional[Any]=None,
        prefix: str="",
        data: Optional[Dict]=None,
        meta: Optional[Dict]=None,
        **kwargs
        ) -> None:
        """
        Initialize ``QuartForm`` class.
        """
        super().__init__(formdata, obj, prefix, data, meta, **kwargs)

    @classmethod
    async def create_form(
        cls,
        formdata: Union[object, MultiDict, CombinedMultiDict, ImmutableMultiDict]=_Auto,
        obj: Optional[Any]=None,
        prefix: str="",
        data: Optional[Dict]=None,
        meta: Optional[Dict]=None,
        **kwargs
        ) -> QuartForm:
        """
        This is a async method will create a new instance of ``QuartForm``.

        This method is primiarly used to intialize the class from submitted
        formdata from ``Quart.request``. If a request is a POST, PUT, PATCH,
        or DELETE method. The form will be intialized using the request. Otherwise
        it will initialized using the defaults. This is required since ``request.files``,
        ``request.form``, and ``request.json`` are coroutines and need to be called in an
        async manner.

        Also, if you are using ``quart_babel`` for translating components of this form, such
        as field labels. This method will call the lazy text as a coroutine, since ``quart_babel``
        use a coroutine to get the locale of of the user.

        """
        # Check if the formdata has not been passed to and if
        # if the form has been submitted. If it has been submitted
        # get it from `quart.request`.
        if formdata is _Auto:
            if _is_submitted():
                formdata = await _get_formdata()
            else:
                formdata = None

        return cls(formdata, obj, prefix, data, meta, **kwargs)

    async def _validate_async(self, validator: Coroutine, field: Field) -> bool:
        """
        Execute async validator.
        """
        try:
            await validator(self, field)
        except ValidationError as error:
            field.errors.append(error.args[0])
            return False
        return True

    async def validate(self, extra_validators: Optional[Dict]=None) -> bool:
        """
        Overload :meth:`validate` to handle custom async validators.
        """
        if extra_validators is not None:
            extra = extra_validators.copy()
        else:
            extra = {}

        async_validators = {}

        # use extra validators to check for StopValidation errors
        completed = []

        def record_status(form, field):
            completed.append(field.name)

        for name, field in self._fields.items():
            func = getattr(self.__class__, f"async_validate_{name}", None)
            if func:
                async_validators[name] = (func, field)
                extra.setdefault[name, []].append(record_status)

        # execute non-async validators
        success = super().validate(extra_validators=extra)

        # execute async validators
        tasks = [self._validate_async(*async_validators[name]) for name in \
            completed]
        async_results = await asyncio.gather(*tasks)

        # check results
        if False in async_results:
            success = False

        return success

    def is_submitted(self) -> bool:
        """
        Consider the form submitted if there is an active request and
        the method is ``POST``, ``PUT``, ``PATCH``, or ``DELETE``.
        """
        return _is_submitted()

    async def validate_on_submit(self, extra_validators: Optional[Dict]=None) -> bool:
        """
        Call :meth:`validate` only if the form is submitted.
        This is a shortcut for ``form.is_submitted() and form.validate()``.
        """
        return self.is_submitted() and \
            await self.validate(extra_validators=extra_validators)

    def hidden_tag(self, *fields) -> Markup:
        """
        Render the form's hidden fields in one call.
        A field is considered hidden if it uses the
        :class:`~wtforms.widgets.HiddenInput` widget.
        If ``fields`` are given, only render the given fields that
        are hidden.  If a string is passed, render the field with that
        name if it exists.
        """
        def hidden_fields(fields):
            for field in fields:
                if isinstance(field, str):
                    field = getattr(self, field, None)

                if field is None or not isinstance(field.widget, HiddenInput):
                    continue

                yield field

        return Markup("\n".join(str(field) for field in hidden_fields(fields or self)))
