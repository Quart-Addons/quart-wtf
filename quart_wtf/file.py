"""
quart_wtf.file

File fields for Quart-WTF.
"""
from collections import abc

from quart.datastructures import FileStorage
from wtforms import FileField as _FileField

from wtforms.validators import (
    DataRequired,
    StopValidation,
    ValidationError
)

class FileField(_FileField):
    """
    Werkzeug-aware subclass of :class:`wtforms.fields.FileField`.
    """
    def process_formdata(self, valuelist) -> None:
        """
        This function processes the formdata for the `FileField`.
        """
        valuelist = (x for x in valuelist if isinstance(x, FileStorage) and x)
        data = next(valuelist, None)

        if data is not None:
            self.data = data
        else:
            self.raw_data = ()

class FileRequired(DataRequired):
    """
    Validates that the data is a :class:`~quart.datastructures.FileStorage` object.
    
    You can also use the synonym ``file_required``.
    
    Argument:
    ---------
        message (``str``): Error message.
    """
    def __call__(self, form, field) -> None:
        if not (isinstance(field.data, FileStorage) and field.data):
            raise StopValidation(
                self.message or field.gettext("This field is required.")
            )

file_required = FileRequired

class FileAllowed:
    """
    Validates that the uploaded file is allowed by a given list of
    extensions or a Quart-Uploads :class:`~quart_uploads.UploadSet`.

    You can also use the synonym ``file_allowed``.

    Argument:
    ---------
        upload_set: A list of extensions or an :class:`~quart_uploads.UploadSet`
    """
    def __init__(self, upload_set, message: str | None = None) -> None:
        self.upload_set = upload_set
        self.message = message

    def __call__(self, form, field) -> None:
        if not (isinstance(field.data, FileStorage) and field.data):
            return

        filename = field.data.filename.lower()

        if isinstance(self.upload_set, abc.Iterable):
            if any(filename.endswith("." + x) for x in self.upload_set):
                return

            raise StopValidation(
                self.message
                or field.gettext(
                    "File does not have an approved extension: {extensions}"
                ).format(extensions=", ".join(self.upload_set))
            )

        if not self.upload_set.file_allowed(filename):
            raise StopValidation(
                self.message
                or field.gettext("File does not have an approved extension.")
            )

file_allowed = FileAllowed

class FileSize:
    """
    Validates that the uploaded file is within a minimum and maximum
    file size (set in bytes).

    You can also use the synonym ``file_size``.

    Arguments:
    ----------
        min_size: minimum allowed file size (in bytes). Defaults to 0 bytes.
        max_size: maximum allowed file size (in bytes).
    """
    def __init__(self, max_size: int, min_size: int=0, message: str | None = None) -> None:
        self.min_size = min_size
        self.max_size = max_size
        self.message = message

    def __call__(self, form, field) -> None:
        if not (isinstance(field.data, FileStorage) and field.data):
            return

        file_size = len(field.data.read())
        field.data.seek(0) # reset cursor position to beginning of file.

        if (file_size < self.min_size) or (file_size > self.max_size):
            # the file is too small or too big => validation error
            raise ValidationError(
                self.message
                or field.gettext(
                    f"File must be between {self.min_size} and {self.max_size} bytes."
                )
            )

file_size = FileSize
