"""
quart_wtf.const

Constant strings for CSRF.
"""
DEFAULT_ENABLED = True

DEFAULT_CHECK_DEFAULT = True

DEFAULT_CSRF_SECRET = None

DEFAULT_CSRF_FIELD_NAME = 'csrf_token'

DEFAULT_CSRF_TIME_LIMIT = 3600

DEFAULT_CSRF_HEADERS = ['X-CSRFToken', 'X-CSRF-Token']

DEFAULT_CSRF_SSL_STRICT = True

DEFAULT_SUBMIT_METHODS = ["POST", "PUT", "PATCH", "DELETE"]

CSRF_NOT_CONFIGURED = "CSRF is not configured.CSRF is not configured."

FIELD_NAME_REQUIRED = "A field name is required to used CSRF."

REFERRER_HEADER = "The referrer header is missing."

REFERRER_HOST = "The referrer does not match the host."

SECRET_KEY_REQUIRED = "A secret key is required to use CSRF."

SESSION_TOKEN_MISSING = "The CSRF session token is missing."

TOKEN_EXPIRED = "The CSRF token has expired."

TOKEN_INVALID = "The CSRF token is invalid"

TOKEN_MISSING = "The CSRF token is missing."

TOKEN_NO_MATCH = "The CSRF tokens do not match."

VALIDATION_FAILED = "CSRF validation failed."
