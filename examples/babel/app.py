"""
Babel Example.
"""
from quart import Quart, render_template
from quart_babel import Babel, lazy_gettext as _
from wtforms import StringField
from wtforms.validators import DataRequired

from quart_wtf import QuartForm

class BabelForm(QuartForm):
    name = StringField(_("Name"), validators=[DataRequired()])

DEBUG = True
SECRET_KEY = "secret"
WTF_18N_ENABLED = True

app = Quart(__name__)
app.config.from_object(__name__)

# Config Babel
babel = Babel(app)

@app.route("/", methods=["GET", "POST"])
async def index():
    """Main Route for example."""
    form = await BabelForm.create_form()

    if await form.validate_on_submit():
        pass

    return await render_template("index.html", form=form)

if __name__ == "__main__":
    app.run()
