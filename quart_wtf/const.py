"""
quart_wtf.const

Constants for Quart-WTF.
"""
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
