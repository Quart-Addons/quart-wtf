"""
Tests CSRF with Quart-WTF.
"""
import pytest
from quart import g, session
from wtforms import ValidationError
from quart_wtf import QuartForm
from quart_wtf.const import (TOKEN_EXPIRED, TOKEN_INVALID, TOKEN_MISSING,
                            TOKEN_NO_MATCH, SESSION_TOKEN_MISSING)
from quart_wtf.utils import generate_csrf, validate_csrf

@pytest.mark.asyncio
async def test_csrf_requires_secret_key(app):
    """
    Test to make sure CSRF requires a secret key.
    """
    async with app.test_request_context("/"):
        # use secret key set by test setup
        generate_csrf()
        # fail with no key
        app.secret_key = None
        pytest.raises(RuntimeError, generate_csrf)
        # use WTF_CSRF config
        app.config["WTF_CSRF_SECRET_KEY"] = "wtf_secret"
        generate_csrf()
        del app.config["WTF_CSRF_SECRET_KEY"]
        # use direct argument
        generate_csrf(secret_key="direct")

@pytest.mark.asyncio
async def test_token_stored_by_generate(app):
    """
    Test token stored.
    """
    async with app.test_request_context("/"):
        generate_csrf()
        assert "csrf_token" in session
        assert "csrf_token" in g

@pytest.mark.asyncio
async def test_custom_token_key(app):
    """
    Test custom token.
    """
    async with app.test_request_context("/"):
        generate_csrf(token_key="oauth_token")
        assert "oauth_token" in session
        assert "oauth_token" in g

@pytest.mark.asyncio
async def test_token_cached(app):
    """
    Test token cached.
    """
    async with app.test_request_context("/"):
        assert generate_csrf() == generate_csrf()

@pytest.mark.asyncio
async def test_validate(app):
    """
    Test validating CSRF.
    """
    async with app.test_request_context("/"):
        validate_csrf(generate_csrf())

@pytest.mark.asyncio
async def test_validation_errors(app):
    """
    Test CSRF validation errors.
    """
    async with app.test_request_context("/"):
        error = pytest.raises(ValidationError, validate_csrf, None)
        assert str(error.value) == TOKEN_MISSING

        error = pytest.raises(ValidationError, validate_csrf, "no session")
        assert str(error.value) == SESSION_TOKEN_MISSING

        token = generate_csrf()
        error = pytest.raises(ValidationError, validate_csrf, token, time_limit=-1)
        assert str(error.value) == TOKEN_EXPIRED

        error = pytest.raises(ValidationError, validate_csrf, "invalid")
        assert str(error.value) == TOKEN_INVALID

        other_token = generate_csrf(token_key="other_csrf")
        error = pytest.raises(ValidationError, validate_csrf, other_token)
        assert str(error.value) == TOKEN_NO_MATCH

@pytest.mark.asyncio
async def test_form_csrf(app, client):
    """
    Test form CSRF.
    """
    @app.route("/", methods=["GET", "POST"])
    async def index():
        form = await QuartForm.create_form()

        if await form.validate_on_submit():
            return "good"

        if form.errors:
            return form.csrf_token.errors[0]

        return form.csrf_token.current_token

    async with app.app_context():
        response = await client.get("/")
        assert await response.get_data(as_text=True) == g.csrf_token

        response = await client.post("/")
        assert  await response.get_data(as_text=True) == "The CSRF token is missing."

        response = await client.post("/", data={"csrf_token": g.csrf_token})
        assert await response.get_data(as_text=True) == "good"

@pytest.mark.asyncio
async def test_validate_error_logged(app, monkeypatch):
    """
    Test validation error is logged.
    """
    from quart_wtf.utils import logger

    async with app.test_request_context("/"):
        messages = []

        def assert_info(message):
            messages.append(message)

        monkeypatch.setattr(logger, "info", assert_info)
        form = QuartForm()
        await form.validate()
        assert len(messages) == 1
        assert messages[0] == TOKEN_MISSING
