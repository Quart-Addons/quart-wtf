import asyncio
from quart import Quart, render_template
from wtforms import PasswordField, SubmitField, StringField, ValidationError
from wtforms.validators import DataRequired, EqualTo
from wtforms.widgets import PasswordInput

from quart_wtf import QuartForm

# DATABASE SETUP
async def db():
    """
    This function mocks a database.
    """
    await asyncio.sleep(0.5)
    userdb = {
        'username': 'testpwd',
        'username2': 'testpwd2'
    }
    return userdb

class UserTable():
    """
    Mock User Table.
    """
    async def get_user_by_username(self, username):
        userdb = await db()
        if username in userdb:
            return userdb[username]
        else:
            raise KeyError

get_repo = UserTable()

async def check_username_is_taken(table: UserTable, username: str):
    """
    Check to see if username is taken. 
    """
    try:
        await table.get_user_by_username(username)
    except KeyError:
        return False
    return True

# FORM SETUP
class CreateAccountForm(QuartForm):
    username = StringField(
        'Username',
        validators=[DataRequired('Please provide username')]
    )

    password = PasswordField(
        'Password',
        widget=PasswordInput(hide_value=False),
        validators=[DataRequired('Please enter your password'), 
                    EqualTo('password_confirm', message='Passwords must match')]
    )

    password_confirm = PasswordField(
        'Confirm Password',
        widget=PasswordInput(hide_value=True),
        validators=[DataRequired("Please confirm your password")]
    )

    submit = SubmitField("Join Now")

    async def async_validate_username(self, username, user_table = get_repo):
        """
        Custom async validation function.
        """
        if await check_username_is_taken(user_table, username.data):
            raise ValidationError('Please use a different username.')

# APP SETUP
DEBUG = True
SECRET_KEY = "secret"

app = Quart(__name__)
app.config.from_object(__name__)

@app.route("/", methods=["GET", "POST"])
async def index():
    form = await CreateAccountForm.create_form()

    if await form.validate_on_submit():
        print("writing to db.")

    return await render_template('index.html', form=form)

if __name__ == "__main__":
    app.run()
