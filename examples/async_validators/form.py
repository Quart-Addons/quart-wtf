"""
Form for async validators example.
"""
from wtforms import PasswordField, SubmitField, StringField, ValidationError
from wtforms.validators import DataRequired, EqualTo
from wtforms.widgets import PasswordInput
from quart_wtf import QuartForm


from .model import UserTable, get_repo, check_username_is_taken

class CreateAccountForm(QuartForm):
    """
    Create account form.
    """
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
        widget=PasswordInput(hide_value=False),
        validators=[DataRequired('Please confirm your password')]
    )

    submit = SubmitField('Join Now')

    async def async_validate_username(self, username, user_table: UserTable=get_repo):
        """
        Custom async validator to check if username is taken.
        """
        if await check_username_is_taken(user_table, username.data):
            raise ValidationError('Please use a different username.')
