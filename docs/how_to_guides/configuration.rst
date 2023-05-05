.. _configuration:

=============
Configuration
=============

Configuration Values
--------------------

.. list-table:: Configuration Variables
    :widths: auto 
    :header-rows: 1

    * - Variable
      - Type
      - Default
      - Description
    * - ``WTF_CSRF_ENABLED``
      - ``bool``
      - ``True``
      - Set to ``False`` to disable all CSRF protection.
    * - ``WTF_CSRF_CHECK_DEFAULT``
      - ``bool``
      - ``True``
      - When using the CSRF protection extension, this contols whether
        every view is protected by default.
    * - ``WTF_CSRF_SECRET_KEY``
      - ``Any``
      - ``quart.Quart.secret_key``
      - Random data for generating secure tokens. If this is not set then
        ``SECRET_KEY`` is used.
    * - ``WTF_CSRF_METHODS``
      - ``list``
      - ``['POST', 'PUT', 'PATCH', 'DELETE']``
      - HTTP methods to protect from CSRF.
    * - ``WTF_CSRF_FIELD_NAME``
      - ``str``
      - ``csrf_token``
      - Name of the form field and session key that holds the CSRF token.
    * - ``WTF_CSRF_HEADERS``
      - ``list``
      - ``['X-CSRFToken', 'X-CSRF-Token']``
      - HTTP headers to search for CSRF token when it is not provided in
        the form.
    * - ``WTF_CSRF_TIME_LIMIT``
      - ``int`` | ``None``
      - ``3600``
      - Max age in seconds for CSRF tokens. If set to ``None``, the CSRF token
        is valid for the life of the session.
    * - ``WTF_CSRF_SSL_STRICT``
      - ``bool``
      - ``True``
      - Determines to enforce the same orgin policy by checking that the referrer
        matches the host. Only applies to HTTPS requests.
    * - ``WTF_I18N_ENABLED``
      - ``bool``
      - ``True``
      - Set to ``False`` to disable `Quart-Babel <https://github.com/Quart-Addons/quart-babel>`_ I18N support.
        Also, set to ``False`` if you want to use WTForms's built-in messages directly, see more info 
        `here <https://wtforms.readthedocs.io/en/stable/i18n.html#using-the-built-in-translations-provider>`_.
  
Logging
-------

CSRF errors are logged at the ``INFO`` level to the ``quart_wtf.csrf`` logger.
You still need to configure logging in your application in order to see these
messages.