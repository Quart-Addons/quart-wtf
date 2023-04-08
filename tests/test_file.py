"""
Tests file handing with Quart-WTF.
"""
import pytest
from quart import Quart
from quart.datastructures import FileStorage
from werkzeug.datastructures import MultiDict
from wtforms import FileField as BaseFileField

from quart_uploads import UploadSet, configure_uploads
from quart_wtf import QuartForm
from quart_wtf.file import FileAllowed, FileField, FileRequired, FileSize

class UploadForm(QuartForm):
    """
    Test upload form.
    """
    class Meta:
        """
        Disable CSRF.
        """
        csrf = False

    file = FileField()

@pytest.mark.asyncio
async def test_process_formdata(app: Quart) -> None:
    """
    Tests prcessing formdata with files.
    """
    async with app.test_request_context("/"):
        formdata = MultiDict((("file", FileStorage()),))
        assert UploadForm(formdata=formdata).file.data is None
        formdata = MultiDict((("file", FileStorage(filename="real")),))
        assert UploadForm(formdata=formdata).file.data is not None

@pytest.mark.asyncio
async def test_file_required(app: Quart) -> None:
    """
    Tests file required.
    """
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
async def test_file_allowed(app: Quart) -> None:
    """
    Tests if a file is allowed.
    """
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
async def test_file_allowed_uploadset(app: Quart, tmp_path) -> None:
    """
    Test Quart-WTF with Quart-Uploads.
    """
    dir = tmp_path / "uploads"
    dir.mkdir()

    app.config["UPLOADS_DEFAULT_DEST"] = dir
    txt = UploadSet("txt", extensions=("txt",))
    configure_uploads(app, txt)
    UploadForm.file.kwargs["validators"] = [FileAllowed(txt)]

    async with app.app_context():
        form = UploadForm()
        assert await form.validate()

        form = UploadForm(file=FileStorage(filename="test.txt"))
        assert await form.validate()

        form = UploadForm(file=FileStorage(filename="test.png"))
        assert not await form.validate()
        assert form.file.errors[0] == "File does not have an approved extension."

@pytest.mark.asyncio
async def test_file_size_no_file_passes_validation(app: Quart) -> None:
    """
    Tests file size validator.
    """
    UploadForm.file.kwargs["validators"] = [FileSize(max_size=100)]

    async with app.test_request_context("/"):
        form = UploadForm()
        assert await form.validate()

@pytest.mark.asyncio
async def test_file_size_small_file_passes_validation(app: Quart, tmp_path) -> None:
    """
    Tests small file size.
    """
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
    app: Quart, min_size, max_size, invalid_file_size, tmp_path
) -> None:
    """
    Tests invalid file size.
    """
    UploadForm.file.kwargs["validators"] = [FileSize(min_size=min_size, max_size=max_size)]

    async with app.test_request_context("/"):
        path = tmp_path / "test_file_invalid_size.txt"
        path.write_bytes(b"\0"  * invalid_file_size)

        with path.open("rb") as file:
            form = UploadForm(file=FileStorage(file))
            assert not await form.validate()
            assert form.file.errors[0] == f"File must be between {min_size} and {max_size} bytes."

@pytest.mark.asyncio
async def test_validate_base_field(app: Quart) -> None:
    """
    Test validating file base field.
    """
    class Form(QuartForm):
        """
        Form for testing.
        """
        class Meta:
            """
            Disable CSRF.
            """
            csrf = False

        f = BaseFileField(validators=[FileRequired()])

    async with app.test_request_context("/"):
        form = Form()
        assert not await form.validate()

        form = Form(f=FileStorage())
        assert not await form.validate()

        form = Form(f=FileStorage(filename="real"))
        assert await form.validate()
