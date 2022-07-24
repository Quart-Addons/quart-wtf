"""
Tests custom validators with Quart-WTF.
"""
import pytest
from wtforms import StringField
from wtforms.validators import ValidationError

from quart_wtf import QuartForm

class FormWithCustomValidators(QuartForm):
    field1 = StringField()
    field2 = StringField()

    def validate_field1(self, field):
        if not field.data == 'value1':
            raise ValidationError('Field value is incorrect.')

    def validate_field2(self, field):
        if not field.data == 'value2':
            raise ValidationError('Field value is incorrect.')

@pytest.mark.asyncio
async def test_custom_validator_success(app, client):
    @app.route('/', methods=['POST'])
    async def index():
        form = await FormWithCustomValidators.from_formdata()
        assert form.field1.data == 'value1'
        assert form.field2.data == 'value2'

        # validate and check again
        success = await form.validate()
        assert success == True

        # check values and errors
        assert form.field1.data == 'value1'
        assert 'field1' not in form.errors

        assert form.field2.data == 'value2'
        assert 'field2' not in form.errors

    await client.post('/', data={'field1': 'value1', 'field2': 'value2'})

@pytest.mark.asyncio
async def test_custom_validator_failure(app, client):
    @app.route('/', methods=['POST'])
    async def index():
        form = await FormWithCustomValidators.from_formdata()
        assert form.field1.data == 'xxx1'
        assert form.field2.data == 'xxx2'

        success = await form.validate()
        assert success == False

        # check values and errors
        assert form.field1.data == 'xxx1'
        assert 'field1' in form.errors

        assert form.field2.data == 'xxx2'
        assert 'field2' in form.errors

    await client.post('/', data={'field1': 'xxx1', 'field2': 'xxx2'})
