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
        assert UploadForm(MultiDict((("file", FileStorage()),))).file.data is None
        assert (
            UploadForm(MultiDict((("file", FileStorage(filename="real")),))).file.data is not None
        )

@pytest.mark.asyncio
async def test_file_required(app):
    UploadForm.file.kwargs["validators"] = [FileRequired()]

    async with app.test_request_context("/"):
        form = UploadForm()
        assert not await form.validate()
        assert form.file.errors[0] == "This field is required."

        form = UploadForm(file="not a file")
        assert not await form.validate()
        assert form.file.errors[0] == "This field is required."

        form = UploadForm(file=FileStorage())
        assert not await form.validate()

        form = UploadForm(file=FileStorage(filename="real"))
        assert await form.validate()

@pytest.mark.asyncio
async def test_file_allowed(app):
    UploadForm.file.kwargs["validators"] = [FileAllowed(("txt",))]

    async with app.test_request_context("/"):
        form = UploadForm()
        assert await form.validate()

        form = UploadForm(file=FileStorage(filename="test.txt"))
        assert await form.validate()

        form = UploadForm(file=FileStorage(filename="test.png"))
        assert not await form.validate()
        assert form.file.errors[0] == "File does not have an approved extension: txt"

@pytest.mark.asyncio
async def test_file_size_no_file_passes_validation(app):
    UploadForm.file.kwargs["validators"] = [FileSize(max_size=100)]
    
    async with app.test_request_context("/"):
        form = UploadForm()
        assert await form.validate()

@pytest.mark.asyncio
async def test_file_size_small_file_passes_validation(app, tmp_path):
    UploadForm.file.kwargs["validators"] = [FileSize(max_size=100)]

    async with app.test_request_context("/"):
        path = tmp_path / "test_file_smaller_than_max.txt"
        path.write_bytes(b"\0")

        with path.open("rb") as file:
            form = UploadForm(file=FileStorage(file))
            assert await form.validate()


@pytest.mark.parametrize(
    "min_size, max_size, invalid_file_size", [(1, 100, 0), (0, 100, 101)]
)

@pytest.mark.asyncio
async def test_file_size_invalid_file_size_fails_validation(
    app, min_size, max_size, invalid_file_size, tmp_path
):
    UploadForm.file.kwargs["validators"] = [FileSize(min_size=min_size, max_size=max_size)]

    async with app.test_request_context("/"):
        path = tmp_path / "test_file_invalid_size.txt"
        path.write_bytes(b"\0"  * invalid_file_size)

        with path.open("rb") as file:
            form = UploadForm(file=FileStorage(file))
            assert not await form.validate()
            assert form.file.errors[0] == f"File must be between {min_size} and {max_size} bytes."

@pytest.mark.asyncio
async def test_validate_base_field(app):
    class Form(QuartForm):
        class Meta:
            csrf = False

        f = BaseFileField(validators=[FileRequired()])

    async with app.test_request_context("/"):
        form = Form()
        assert not await form.validate()

        form = Form(f=FileStorage())
        assert not await form.validate()

        form = Form(f=FileStorage(filename="real"))
        assert await form.validate()
