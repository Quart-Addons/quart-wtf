.. _forms:

==============
Creating Forms
==============

The QuartForm Class
-------------------

Quart-WTF provides a form class that makes it easy to add form validation and CSRF protection to Quart apps. To make a form, 
subclass the `QuartForm` class and use [WTForms](https://wtforms.readthedocs.io/) fields, validators and widgets to define the inputs. 
The `QuartForm` class inherits from the WTForms `Form` class so you can use WTForms features and methods to add more advanced functionality 
to your app:

.. code-block:: python

    from quart-wtf import QuartForm
    from wtforms import TextField, PasswordField 
    from wtforms.validators import DataRequired, Email, EqualTo
    from wtforms.widgets import PasswordInput

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

Since the Quart provides awaitable form objects in `request`. You
will need to use :meth:`~quart_wtf.QuartForm.create_form` async class method, which will
get the form objects using default values on GET requests and formdata 
on POST requests. 

.. code-block:: python
    @app.route('/create-account', methods=['GET', 'POST'])
    async def create_account():
        """GET|POST /create-account: Create account form handler
        """
        form = await CreateAccountForm.create_form()
        return await render_template('creataccount.html', form=form)

Secure Forms
------------

Without any configuration, the :class:`QuartForm` will be a session secure
form with csrf protection. We encourage you not to change this.

If you would like to disable the CSRF protection. Then you can pass:

.. code-block:: python

    form = await QuartForm.create_form(meta={'csrf': False})

You can also disable it globally. Though you shouldn't with the
configuration.

.. code-block:: python

    WTF_CSRF_ENABLED = False

In order to generate the csrf token, you must have a secret key, this
is usually the same as your Flask app secret key. If you want to use
another secret key, config it:

.. code-block:: python

    WTF_CSRF_SECRET_KEY = 'a random string'

File Uploads
------------

The :class:`FileField` provided by Flask-WTF differs from the WTForms-provided
field. It will check that the file is a non-empty instance of
:class:`~quart.datastructures.FileStorage`, otherwise ``data`` will be
``None``:

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

Remember to set the ``enctype`` of the HTML form to
``multipart/form-data``, otherwise ``request.files`` will be empty.

.. code-block:: html

    <form method="POST" enctype="multipart/form-data">
        ...
    </form>

Quart-WTF handles passing form data to the form for you.
If you pass in the data explicitly, remember that ``request.form`` must
be combined with ``request.files`` for the form to see the file data:

.. code-block:: python 

    form = await PhotoForm().create_form()
    
    # is equivalent to:

    from quart import request
    from werkzeug.datastructures import CombinedMultiDict

    form_data = await request.form 
    files = await request.files
    formdata = CombinedMultiDict((files, form_data))
    form = PhotoForm(formdata=formdata)

Validation
----------

The `QuartForm` class has a useful `.validate_on_submit()` method that performs input validation for 
POST, PUT, PATCH and DELETE requests and returns a boolean indicating whether or not there were any errors. 
After validation, errors are available via the `.errors` attribute attached to each input field instance. 
Note that validation is asynchronous to handle async field validators (see below):

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

Async Custom validators
-----------------------

The `QuartForm` class allows you to implement asynchronous [WTForms-like custom validators](https://wtforms.readthedocs.io/en/stable/validators/#custom-validators) 
by adding `async_validate_{fieldname}` methods to your form classes:

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

File Uploading Validation
-------------------------

Quart-WTF supports validating file uploads with
:class:`FileRequired` and :class:`FileAllowed`. They can be used with both
Quart-WTF's and WTForms's ``FileField`` classes.

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