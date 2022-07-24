"""
Tests async validators with Quart-WTF.
"""
import asyncio
import pytest
from wtforms import StringField
from wtforms.validators import DataRequired, ValidationError

from quart_wtf import QuartForm

class FormWithAsyncValidators(QuartForm):
    field1 = StringField()
    field2 = StringField(validators=[DataRequired()])

    async def async_validate_field1(self, field):
        # test await
        await asyncio.sleep(.01)

        #raise exception
        if not field.data == 'value1':
            raise ValidationError('Field value is not correct.')

    async def async_validate_field2(self, field):
        # test await
        await asyncio.sleep(.02)

        #raise exception
        if not field.data == 'value2':
            raise ValidationError('Field value is not correct.')

class FormWithAsyncException(QuartForm):
    field1 = StringField()

    async def async_validate_field1(self, field):
        await asyncio.sleep(.01)
        raise Exception('test')

@pytest.mark.asyncio
async def test_async_validator_success(app, client):
    @app.route('/', methods=['POST'])
    async def index():
        form = await FormWithAsyncValidators.from_formdata()
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
async def test_async_validator_error(app, client):
    @app.route('/', methods=['POST'])
    async def index():
        form = await FormWithAsyncValidators.from_formdata()
        assert form.field1.data == 'xxx1'
        assert form.field2.data == 'xxx2'

        # validate and check again
        success = await form.validate()
        assert success == False
        assert form.field1.data == 'xxx1'
        assert form.field2.data == 'xxx2'

        # check errors
        assert len(form.errors['field1']) == 1
        assert form.errors['field1'][0] == 'Field value is incorrect.'

        assert len(form.errors['field2']) == 1
        assert form.errors['field2'][0] == 'Field value is incorrect.'

    await client.post('/', data={'field1': 'xxx1', 'field2': 'xxx2'})

@pytest.mark.asyncio
async def test_data_required_error(app, client):
    @app.route('/', methods=['POST'])
    async def index():
        form = await FormWithAsyncValidators.from_formdata()
        assert form.field1.data == 'xxx1'
        assert form.field2.data in ["", None]  # WTForms >= 3.0.0a1 is None

        # validate and check again
        success = await form.validate()
        assert success == False
        assert form.field1.data == 'xxx1'

        # check errors
        assert len(form.errors['field1']) == 1
        assert form.errors['field1'][0] == 'Field value is incorrect.'

        assert len(form.errors['field2']) == 1
        assert form.errors['field2'][0] == 'This field is required.'

    await client.post('/', data={'field1': 'xxx1'})

@pytest.mark.asyncio
async def test_async_validator_exception(app, client):
    @app.route('/', methods=['POST'])
    async def index():
        form = await FormWithAsyncException.from_formdata()
        try:
            await form.validate()
        except Exception as err:
            assert err.args[0] == 'test'
        else:
            assert False

    await client.post('/', data={'field1': 'xxx1', 'field2': 'xxx2'})
