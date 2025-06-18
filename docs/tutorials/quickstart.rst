.. _quickstart:

==========
Quickstart
==========

So you can't wait to get started? This page gives you a good introduction to Quart-WTF.
It assumes that you already have Quart-WTF installed. If you do not, head over to the
:doc:`installation` section. 

Creating Forms
--------------

Quart-WTF provides your Quart application integration with WTForms. For example:

.. code-block:: python

    from quart_wtf import QuartForm
    from wtforms import StringField
    from wtforms.validators import DataRequired

    class MyForm(QuartForm):
        name = StringField('name', validators=[DataRequired()])
    
.. note::

    Quart-WTF will not import anything from WTForms, so you will
    need to import fields from WTForms.

In addition, a CSRF token hidden field is created automatically. You can
render this in your template like this:

.. code-block:: html+jinja

    <form method="POST" action="/">
        {{ form.csrf_token }}
        {{ form.name.label }} {{ form.name(size=20) }}
        <input type="submit" value="Go">
    </form>

If you have multiple hidden fields, you can render them in one
block using :meth:`~quart_wtf.QuartForm.hidden_tag`.

.. code-block:: html+jinja

    <form method="POST" action="/">
        {{ form.hidden_tag() }}
        {{ form.name.label }} {{ form.name(size=20) }}
        <input type="submit" value="Go">
    </form>

Since the Quart provides awaitable form objects in `request`. You
will need to use :meth:`~quart_wtf.QuartForm.from_formdata` async class method, which will
get the form objects using default values on GET requests and formdata 
on POST requests. 

.. code-block:: python

    @app.route('/', methods=['GET', 'POST'])
    async def index():
        form = await MyForm.create_form()

        if await form.validate_on_submit():
            return redirect('/success')
        
        return await render_template('index.html', form=form)

Validating Forms
----------------

Validating the request in your routes can be done as shown below. Note that
:meth:`~quart_wtf.QuartForm.validate_on_submit` is an awaitable. 

.. code-block:: python

    @app.route('/', methods=['GET', 'POST'])
    async def index():
        form = await MyForm.create_form()

        if await form.validate_on_submit():
            return redirect('/success')
        
        return await render_template('index.html', form=form)

Note that you don't have to pass the `request.form` to Quart-WTF. It will 
automatically load the formdata from the request. The convenient helper function
`validate_on_submit` will check if it is a POST request and if the form is valid.

If your forms include validation, you'll need to add to your template to display
any error messages.  Using the ``form.name`` field from the example above, that
would look like this:

.. code-block:: html+jinja

    {% if form.name.errors %}
        <ul class="errors">
        {% for error in form.name.errors %}
            <li>{{ error }}</li>
        {% endfor %}
        </ul>
    {% endif %}



