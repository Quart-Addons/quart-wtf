"""
tests.test_custom_validators
"""
import pytest
from quart import Quart
from quart.typing import TestClientProtocol
from wtforms import StringField  # type: ignore
from wtforms.validators import ValidationError  # type: ignore

from quart_wtf import QuartForm


class FormWithCustomValidators(QuartForm):
    """
    Test form to test custom validators.
    """
    field1 = StringField()
    field2 = StringField()

    def validate_field1(self, field):  # type: ignore
        """
        Validates field1.
        """
        if not field.data == 'value1':
            raise ValidationError('Field value is incorrect.')

    def validate_field2(self, field):  # type: ignore
        """
        Validates field2.
        """
        if not field.data == 'value2':
            raise ValidationError('Field value is incorrect.')


@pytest.mark.asyncio
async def test_custom_validator_success(
    app: Quart, client: TestClientProtocol
) -> None:
    """
    Test custom validators with success.
    """
    @app.route('/', methods=['POST'])
    async def index() -> None:
        form = await FormWithCustomValidators().create_form()
        assert form.field1.data == 'value1'
        assert form.field2.data == 'value2'

        # validate and check again
        success = await form.validate()
        assert success is True

        # check values and errors
        assert form.field1.data == 'value1'
        assert 'field1' not in form.errors

        assert form.field2.data == 'value2'
        assert 'field2' not in form.errors

    await client.post('/', form={'field1': 'value1', 'field2': 'value2'})


@pytest.mark.asyncio
async def test_custom_validator_failure(
    app: Quart, client: TestClientProtocol
) -> None:
    """
    Test custom validators with failure.
    """
    @app.route('/', methods=['POST'])
    async def index() -> None:
        form = await FormWithCustomValidators().create_form()
        assert form.field1.data == 'xxx1'
        assert form.field2.data == 'xxx2'

        success = await form.validate()
        assert success is False

        # check values and errors
        assert form.field1.data == 'xxx1'
        assert 'field1' in form.errors

        assert form.field2.data == 'xxx2'
        assert 'field2' in form.errors

    await client.post('/', form={'field1': 'xxx1', 'field2': 'xxx2'})
