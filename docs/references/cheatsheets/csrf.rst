.. _csrf-cheatsheet:

=========================
CSRF Extension Cheatsheet
=========================

Basic App:
----------

.. code-block:: python

    from quart import Quart, render_template
    from quart_wtf import CSRF

    app = Quart(__name__)

    csrf = CSRF(app)

    # Continue setting up the app.

Large App:
----------

.. code-block:: python
    :caption: youapplication/app.py

    from quart import Quart
    from quart_wtf import CSRF

    csrf = CSRF()

    def create_app() -> Quart:
        app = Quart(__name__)

        csrf.init_app(app)

        # Other app registration here. 
        
        return app

Custom Error Response:
----------------------

.. code-block:: python

    from quart_wtf import CSRFError

    @app.errorhandler(CSRFError)
    async def handle_csrf_error(e):
        return await render_template('csrf_error.html', reason=e.description), 400

Exclude Views from Protection:
------------------------------

.. code-block:: python

    @app.route('/foo', methods=('GET', 'POST'))
    @csrf.exempt
    async def my_handler():
        # ...
        return 'ok'

You can exclude all the views of a blueprint as well.

.. code-block:: python 

    csrf.exempt(account_blueprint)