"""
Upload Example.
"""
from quart import Quart, render_template
from wtforms import FieldList

from quart_wtf import QuartForm, FileField

class FileUploadForm(QuartForm):
    uploads = FieldList(FileField())

DEBUG = True
SECRET_KEY = "secret"

app = Quart(__name__)
app.config.from_object(__name__)

@app.route("/", methods=["GET", "POST"])
async def index():
    """Example Main Route."""
    form = await FileUploadForm.create_form()

    for _ in range(5):
        form.uploads.append_entry()

    filedata = []

    if await form.validate_on_submit():
        for upload in form.uploads.entries:
            filedata.append(upload)

    return await render_template("index.html", form=form, filedata=filedata)

if __name__ == "__main__":
    app.run()
