"""
Tests file handing with Quart-WTF.
"""
import pytest
from werkzeug.datastructures import FileStorage
from werkzeug.datastructures import MultiDict
from wtforms import FileField as BaseFileField

from quart_wtf import QuartForm
from quart_wtf.file import FileAllowed, FileField, FileRequired, FileSize

class UploadForm(QuartForm):
    class Meta:
        csrf = False

    file = FileField()

@pytest.mark.asyncio
async def test_process_formdata(app):
    async with app.test_request_context("/"):
        formdata = MultiDict((("file", FileStorage()),))
        form = await UploadForm.from_formdata(formdata)
        assert form.file.data is None
        formdata = MultiDict((("file", FileStorage(filename="real")),))
        form = await UploadForm.from_formdata(formdata)
        assert form.file.data is not None

@pytest.mark.asyncio
async def test_file_required(app):
    class UploadFormRequired(QuartForm):
        class Meta:
            csrf = False
        file = FileField(validators=[FileRequired()])

    async with app.test_request_context("/"):
        form = await UploadFormRequired.from_formdata()
        assert not await form.validate()
        assert form.file.errors[0] == "This field is required."

        formdata = formdata = MultiDict((("file", "not a file"),))
        form = await UploadFormRequired.from_formdata(formdata)
        assert not await form.validate()
        assert form.file.errors[0] == "This field is required."

        formdata = MultiDict((("file", FileStorage()),))
        form = await UploadFormRequired.from_formdata(formdata)
        assert not await form.validate()

        formdata = MultiDict((("file", FileStorage(filename="real")),))
        form = await UploadFormRequired.from_formdata(formdata)
        assert await form.validate()

@pytest.mark.asyncio
async def test_file_allowed(app):
    class UploadFormAllowed(QuartForm):
        class Meta:
            csrf = False
        file = FileField(validators=[FileAllowed("txt")])

    async with app.test_request_context("/"):
        form = await UploadFormAllowed().from_formdata(formdata=None)
        assert await form.validate()

        formdata = MultiDict((("file", FileStorage(filename="text.txt")),))
        form = await UploadFormAllowed().from_formdata(formdata)
        assert await form.validate()

        formdata = MultiDict((("file", FileStorage(filename="test.png")),))
        form = await UploadFormAllowed().from_formdata(formdata)
        assert not await form.validate()
        assert form.file.errors[0] == "File does not have an approved extension: txt"

@pytest.mark.asyncio
async def test_file_size_no_file_passes_validation(form):
    form.file.kwargs["validators"] = [FileSize(max_size=100)]
    f = await form.from_formdata()
    assert await f.validate()


def test_file_size_small_file_passes_validation(form, tmp_path):
    form.file.kwargs["validators"] = [FileSize(max_size=100)]
    path = tmp_path / "test_file_smaller_than_max.txt"
    path.write_bytes(b"\0")

    with path.open("rb") as file:
        f = form(file=FileStorage(file))
        assert f.validate()


@pytest.mark.parametrize(
    "min_size, max_size, invalid_file_size", [(1, 100, 0), (0, 100, 101)]
)

@pytest.mark.asyncio
async def test_file_size_invalid_file_size_fails_validation(
    form, min_size, max_size, invalid_file_size, tmp_path
):
    form.file.kwargs["validators"] = [FileSize(min_size=min_size, max_size=max_size)]
    path = tmp_path / "test_file_invalid_size.txt"
    path.write_bytes(b"\0" * invalid_file_size)
    f = await form.from_formdata()

    with path.open("rb") as file:
        f = f(file=FileStorage(file))
        assert not f.validate()
        assert f.file.errors[
            0
        ] == "File must be between {min_size} and {max_size} bytes.".format(
            min_size=min_size, max_size=max_size
        )

@pytest.mark.asyncio
async def test_validate_base_field(app):
    class Form(QuartForm):
        class Meta:
            csrf = False

        f = BaseFileField(validators=[FileRequired()])

    async with app.test_request_context("/"):
        form = await Form.from_formdata(formdata=None)
        assert not await form.validate()

        formdata = MultiDict((("f", FileStorage()),))
        form = await Form.from_formdata(formdata)
        assert not await form.validate()

        formdata = MultiDict((("f", FileStorage(filename="real")),))
        form = await Form.from_formdata(formdata)
        assert await form.validate()
