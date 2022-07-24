"""
Quart-WTF Form
"""
import asyncio

from quart import current_app, session
from wtforms import Form, ValidationError
from wtforms.meta import DefaultMeta
from werkzeug.utils import cached_property

from .csrf import _QuartFormCSRF
from .utils import _is_submitted, _get_formdata

_Auto = object()

class QuartForm(Form):
    """
    Quart specific subclass of WTForms :class:`~wtforms.form.Form`.
    To populate from submitted formdata use the ```.from_submit()``` class
    method to initialize the instance.
    """
    class Meta(DefaultMeta):
        """
        Meta class for Quart specific subclass of WTForms.
        """
        csrf_class = _QuartFormCSRF
        csrf_context = session

        @cached_property
        def csrf(self):
            """
            Determines if CSRF is enabled.
            """
            return current_app.config.get("WTF_CSRF_ENABLED", True)

        @cached_property
        def csrf_secret(self):
            """
            CSRF secret key.
            """
            return current_app.config.get("WTF_CSRF_SECRET_KEY", current_app.secret_key)

        @cached_property
        def csrf_field_name(self):
            """
            CSRF field name.
            """
            return current_app.config.get("WTF_CSRF_FIELD_NAME", "csrf_token")

        @cached_property
        def csrf_time_limit(self):
            """
            CSRF time limit.
            """
            return current_app.config.get("WTF_CSRF_TIME_LIMIT", 3600)

    def __init__(self, *args, formdata=_Auto, **kwargs) -> None:
        super().__init__(formdata, *args, **kwargs)

    @classmethod
    async def from_formdata(cls, *args, formdata=_Auto, **kwargs):
        """
        Method to support initializing from submitted formdata.
        """
        if formdata is _Auto:
            if _is_submitted():
                formdata = await _get_formdata()
            else:
                formdata = None

        return cls(formdata=formdata, *args, **kwargs)

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
