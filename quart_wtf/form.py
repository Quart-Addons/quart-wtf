"""
quart_wtf.form
"""
from __future__ import annotations
import asyncio
from typing import Any, Callable, Dict, List

from markupsafe import Markup
from quart import request
from werkzeug.datastructures import CombinedMultiDict, ImmutableMultiDict
from wtforms import Form, Field, ValidationError
from wtforms.widgets import HiddenInput

from .const import SUBMIT_METHODS
from .meta import QuartFormMeta
from .typing import FormData


_Auto = object()


class QuartForm(Form):
    """
    Quart specific subclass of WTForms :class:`~wtforms.form.Form`.
    To populate from submitted formdata use the ```.create_form``` class
    method to initialize the instance.

    Arguments:
            formdata: Input data coming from the client, usually
            ``request.form`` or equivalent. Should provide a "multi
            dict" interface to get a list of values for a given key.

            obj: Take existing data from attributes on this object
            matching form field attributes. Only used if ``formdata`` is
            not passed.

            prefix: If provided, all fields will have their name
            prefixed with the value. This is for distinguishing multiple
            forms on a single page. This only affects the HTML name for
            matching input data, not the Python name for matching
            existing data.

            data: Take existing data from keys in this dict matching
            form field attributes. ``obj`` takes precedence if it also
            has a matching attribute. Only used if ``formdata`` is not
            passed.

            meta: A dict of attributes to override on this form's
            :attr:`meta` instance.

            extra_filters: A dict mapping field attribute names to
            lists of extra filter functions to run. Extra filters run
            after filters passed when creating the field. If the form
            has ``filter_<fieldname>``, it is the last extra filter.

            kwargs: Merged with ``data`` to allow passing existing
            data as parameters. Overwrites any duplicate keys in
            ``data``. Only used if ``formdata`` is not passed.
    """
    Meta = QuartFormMeta

    @classmethod
    async def create_form(
        cls,
        formdata: object | FormData = _Auto,
        obj: Any | None = None,
        prefix: str = "",
        data: Dict | None = None,
        meta: Dict | None = None,
        **kwargs: Dict[str, Any]
    ) -> QuartForm:
        """
        This creates a new instance of the form and can only be called within
        your applications routes.

        This method is primiarly used to intialize the class from submitted
        formdata from ``Quart.request``. If a request is a POST, PUT, PATCH,
        or DELETE method. The form will be intialized using the request.
        Otherwise it will initialized using the defaults. This is required
        since ``request.files``, ``request.form``, and ``request.json`` are
        coroutines and need to be called in an async manner.

        Arguments:
            formdata: Input data coming from the client, usually
            ``request.form`` or equivalent. Should provide a "multi
            dict" interface to get a list of values for a given key.

            obj: Take existing data from attributes on this object
            matching form field attributes. Only used if ``formdata`` is
            not passed.

            prefix: If provided, all fields will have their name
            prefixed with the value. This is for distinguishing multiple
            forms on a single page. This only affects the HTML name for
            matching input data, not the Python name for matching
            existing data.

            data: Take existing data from keys in this dict matching
            form field attributes. ``obj`` takes precedence if it also
            has a matching attribute. Only used if ``formdata`` is not
            passed.

            meta: A dict of attributes to override on this form's
            :attr:`meta` instance.

            extra_filters: A dict mapping field attribute names to
            lists of extra filter functions to run. Extra filters run
            after filters passed when creating the field. If the form
            has ``filter_<fieldname>``, it is the last extra filter.

            kwargs: Merged with ``data`` to allow passing existing
            data as parameters. Overwrites any duplicate keys in
            ``data``. Only used if ``formdata`` is not passed.
        """
        if cls.is_submitted():
            if formdata is _Auto:
                files = await request.files
                form = await request.form

                if files:
                    formdata = CombinedMultiDict((files, form))
                elif form:
                    formdata = form
                elif request.is_json:
                    json = await request.json
                    formdata = ImmutableMultiDict(json)
                else:
                    formdata = None
        else:
            formdata = None

        return cls(formdata, obj, prefix, data, meta, **kwargs)

    async def _validate_async(
            self, validator: Callable, field: Field
    ) -> bool:
        """
        Execute async validators.
        """
        errors = list(field.errors)

        try:
            await validator(self, field)
        except ValidationError as error:
            errors.append(error.args[0])
            field.errors = tuple(errors)
            return False
        return True

    async def validate(
            self, extra_validators: Dict[str, List[Callable]] = None
    ) -> bool:
        # pylint: disable=W0236
        """
        Async Overload :meth:`validate` to handle custom async validators.

        Arguments:
            extra_validators: Extra form validators.
        """
        if extra_validators is not None:
            extra = extra_validators.copy()
        else:
            extra = {}

        async_validators = {}
        completed = []

        def record_status(_, field):
            completed.append(field.name)

        # Check for inline async validators
        for name, field in self._fields.items():
            func = getattr(self.__class__, f'async_validator_{name}', None)
            if func:
                async_validators[name] = (func, field)
                extra.setdefault(name, []).append(record_status)

        # execute non-async validators
        success = super().validate(extra_validators=extra_validators)

        # execute async validators
        if async_validators:
            tasks = [self._validate_async(*async_validators[name]) for
                     name in completed]
            async_results = await asyncio.gather(*tasks)

            if False in async_results:
                success = False

        return success

    @staticmethod
    def is_submitted() -> bool:
        """
        Consider the form submitted if there is an active request and
        the method is ``POST``, ``PUT``, ``PATCH``, or ``DELETE``.
        """
        return bool(request) and request.method in SUBMIT_METHODS

    async def validate_on_submit(
            self, extra_validators: Dict[str, Any] | None = None
    ) -> bool:
        """
        Call :meth:`validate` only if the form is submitted.
        This is a shortcut for ``QuartForm.is_submitted and
        ``QuartForm.validate()``.

        Arguments:
            extra_validators: Extra form validators.
        """
        return self.is_submitted() and \
            await self.validate(extra_validators=extra_validators)

    def hidden_tag(self, *fields) -> Markup:  # type: ignore
        """
        Render the form's hidden fields in one call.
        A field is considered hidden if it uses the
        :class:`~wtforms.widgets.HiddenInput` widget.
        If ``fields`` are given, only render the given fields that
        are hidden.  If a string is passed, render the field with that
        name if it exists.

        Argument:
            fields: Form fields.
        """
        def hidden_fields(fields):  # type: ignore
            for field in fields:
                if isinstance(field, str):
                    field = getattr(self, field, None)

                if field is None or not isinstance(field.widget, HiddenInput):
                    continue

                yield field

        return Markup("\n".join(str(field) for field
                                in hidden_fields(fields or self)))
