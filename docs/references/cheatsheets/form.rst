.. _form-cheatsheet:

===============
Form Cheatsheet
===============

General Features:
-----------------

Refer to the official WTForms documentation.

Configuration Variables:
------------------------

.. code-block:: python
    :caption: app.py 

    from quart import Quart

    # Some configuration variables below are shown
    # as non-default values for example purposes.
    # Also, not all configuration variables are shown.
    WTF_CSRF_ENABLED = True
    WTF_CSRF_CHECK_DEFAULT = False
    WTF_CSRF_SECRET_KEY = 'CSRFProtectsTheApp'
    WTF_I18N_ENABLED = False

    app = Quart(__name__)
    app.config.from_pyfile(__name__)

    # Setup the rest of the app & create forms.

Creating Forms:
---------------

.. code-block:: python

    from quart-wtf import QuartForm
    from wtforms import TextField, PasswordField 
    from wtforms.validators import DataRequired, Email, EqualTo
    from wtforms.widgets import PasswordInput

    class CreateAccountForm(StarletteForm):
        email = TextField(
            'Email address',
            validators=[
                DataRequired('Please enter your email address'),
                Email()
            ]
        )

        password = PasswordField(
            'Password',
            widget=PasswordInput(hide_value=False),
            validators=[
                DataRequired('Please enter your password'),
                EqualTo('password_confirm', message='Passwords must match')
            ]
        )

        password_confirm = PasswordField(
            'Confirm Password',
            widget=PasswordInput(hide_value=False),
            validators=[
                DataRequired('Please confirm your password')
            ]
        )

Calling in Routes:
------------------

.. code-block:: python
    
    @app.route('/create-account', methods=['GET', 'POST'])
    async def create_account():
        """GET|POST /create-account: Create account form handler
        """
        form = await CreateAccountForm.create_form()

        if await form.validate_on_submit():
            # Do what you need to do with the data.
            pass

        return await render_template('creataccount.html', form=form)

File Uploads:
-------------

.. code-block:: python

    from quart_wtf import QuartForm, FileField, FileRequired
    from werkzeug.utils import secure_filename

    class PhotoForm(QuartForm):
        photo = FileField(validators=[FileRequired()])

    @app.route('/upload', methods=['GET', 'POST'])
    async async def upload():
        form = await PhotoForm().create_form()

        if await form.validate_on_submit():
            f = form.photo.data
            filename = secure_filename(f.filename)
            f.save(os.path.join(
                app.instance_path, 'photos', filename
            ))
            return redirect(url_for('index'))

        return await render_template('upload.html', form=form)

Form Validation:
----------------

.. code-block:: python 

    @app.route('/create-account', methods=['GET', 'POST'])
    async def create_account():
        """GET|POST /create-account: Create account form handler
        """
        # initialize form
        form = await CreateAccountForm.create_form()

        # validate form
        if await form.validate_on_submit():
            # TODO: Save account credentials before returning redirect response
            return redirect(url_for('index'))

        return await render_template('creataccount.html', form=form)

Form Async Custom Validators:
-----------------------------

.. code-block:: python 

    from quart_wtf import QuartForm
    from wtforms import TextField, PasswordField, ValidationError
    from wtforms.validators import DataRequired, Email, EqualTo


    class CreateAccountForm(QuartForm):
        email = TextField(
            'Email address',
            validators=[
                DataRequired('Please enter your email address'),
                Email()
            ]
        )

        password = PasswordField(
            'Password',
            widget=PasswordInput(hide_value=False),
            validators=[
                DataRequired('Please enter your password'),
                EqualTo('password_confirm', message='Passwords must match')
            ]
        )

        password_confirm = PasswordField(
            'Confirm Password',
            widget=PasswordInput(hide_value=False),
            validators=[
                DataRequired('Please confirm your password')
            ]
        )

        async def async_validate_email(self, field):
            """Asynchronous validator to check if email is already in-use
            """
            # replace this with your own code
            if await make_database_request_here():
                raise ValidationError('Email is already in use')

File Uploading Validation:
--------------------------

:class:`FileAllowed` works well with Quart-Uploads:

.. code-block:: python

    from quart_uploads import UploadSet, IMAGES
    from flask_wtf import FlaskForm
    from flask_wtf.file import FileField, FileAllowed, FileRequired

    images = UploadSet('images', IMAGES)

    class UploadForm(QuartForm):
        upload = FileField('image', validators=[
            FileRequired(),
            FileAllowed(images, 'Images only!')
        ])

It can also be used without Quart-Uploads by passing the extensions directly:

.. code-block:: python

    class UploadForm(FlaskForm):
        upload = FileField('image', validators=[
            FileRequired(),
            FileAllowed(['jpg', 'png'], 'Images only!')
        ])
