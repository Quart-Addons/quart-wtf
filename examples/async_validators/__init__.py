"""
Main file for async validator example.
"""
from quart import Quart, render_template
from .form import CreateAccountForm

app = Quart(__name__)
app.config.update({
    "TESTING": True,
    "SECRET-KEY": __name__,
})

@app.route("/", methods=['GET', 'POST'])
async def index():
    """
    Main App Route.
    """
    form = await CreateAccountForm.from_formdata()

    if await form.validate_on_submit():
        print('writing to db.')

    return await render_template('index.html', form=form)

def run() -> None:
    """
    Runs the app. 
    """
    app.run()
