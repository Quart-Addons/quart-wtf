"""
Quart-WTF Form
"""
from __future__ import annotations
import asyncio
from markupsafe import Markup
from wtforms import Form, ValidationError
from wtforms.widgets import HiddenInput

from .meta import _QuartFormMeta
from .utils import _is_submitted, _get_formdata

_Auto = object()

class QuartForm(Form):
    """
    Quart specific subclass of WTForms :class:`~wtforms.form.Form`.
    To populate from submitted formdata use the ```.from_submit()``` class
    method to initialize the instance.
    """
    Meta = _QuartFormMeta

    def __init__(self, *args, formdata=None, **kwargs) -> None:
        """
        Initialize the form. Takes all the same parameters as WTForms
        base form.
        """
        super().__init__(formdata=formdata, *args, **kwargs)

    @classmethod
    async def from_formdata(cls, *args, formdata=_Auto, **kwargs) -> QuartForm:
        """
        Method to support initializing class from submitted formdata. If
        request is a POST, PUT, PATCH or DELETE, form will be initialized using
        formdata. Otherwise, it will be initialized using defaults.

        Since the `request.files`, `request.form` & `request.json` are coroutines.
        a classmethod is need to set the formdata for a given request.

        Args:
            formdata (ImmutableMultiDict, optional): If present, this will be used
                to initialize the form fields.
            prefix (str): The prefix to be used for the fields.

        Returns:
            :class:`quart_wtf.form.QuartForm`: A new instance of the form.
        """
        if formdata is _Auto:
            if _is_submitted():
                formdata = await _get_formdata()
            else:
                formdata = None

        return cls(*args, formdata=formdata, **kwargs)

    async def _validate_async(self, validator, field) -> bool:
        """
        Execute async validator.
        """
        try:
            await validator(self, field)
        except ValidationError as error:
            field.errors.append(error.args[0])
            return False
        return True

    async def validate(self, extra_validators=None) -> bool:
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

    async def validate_on_submit(self, extra_validators=None):
        """
        Call :meth:`validate` only if the form is submitted.
        This is a shortcut for ``form.is_submitted() and form.validate()``.
        """
        return self.is_submitted() and \
            await self.validate(extra_validators=extra_validators)

    def hidden_tag(self, *fields):
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
