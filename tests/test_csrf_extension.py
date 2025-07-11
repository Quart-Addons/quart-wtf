"""
tests.test_csrf_extension
"""
from typing import Any, List
import pytest
from quart import Quart, Blueprint, g, render_template_string, Response
from quart.typing import TestClientProtocol

from quart_wtf import CSRFError, CSRFProtect, QuartForm
from quart_wtf.const import REFERRER_HEADER, REFERRER_HOST, TOKEN_MISSING
from quart_wtf.utils import logger, generate_csrf

# pylint: skip-file


@pytest.fixture
def app(app: Quart) -> Quart:  # pylint: disable=W0621
    """
    App fixture for testing the CSRF extension.
    """
    app.secret_key = "some_secret_you_would_not_guess"
    CSRFProtect(app)

    @app.route("/", methods=["GET", "POST"])
    async def index() -> None:
        pass

    @app.after_request
    async def add_csrf_header(response: Response) -> Response:
        response.headers.set("X-CSRF-Token", generate_csrf())
        return response

    return app


@pytest.fixture
def csrf(app: Quart) -> CSRFProtect:
    """
    Returns the CSRF extension.
    """
    return app.extensions["csrf"]


@pytest.mark.asyncio
async def test_render_token(app: Quart) -> None:
    """
    Tests rendering the CSRF token.
    """
    async with app.test_request_context("/"):
        token = generate_csrf()
        assert await render_template_string("{{ csrf_token() }}") == token


@pytest.mark.asyncio
async def test_protect(app: Quart, client: TestClientProtocol) -> None:
    """
    Tests CSRF protection.
    """
    await app.startup()

    response = await client.post("/")
    assert response.status_code == 400
    data = await response.get_data(as_text=True)
    assert TOKEN_MISSING in data

    app.config["WTF_CSRF_ENABLED"] = False
    response = await client.post("/")
    data = await response.get_data()
    assert data == b""
    app.config["WTF_CSRF_ENABLED"] = True

    app.config["WTF_CSRF_CHECK_DEFAULT"] = False
    response = await client.post("/")
    data = await response.get_data()
    assert data == b""
    app.config["WTF_CSRF_CHECK_DEFAULT"] = True

    response = await client.options("/")
    assert response.status_code == 200
    response = await client.post("/not-found")
    assert response.status_code == 404

    response = await client.get("/")
    assert response.status_code == 200
    token = response.headers["X-CSRF-Token"]
    response = await client.post("/", form={"csrf_token": token})
    assert response.status_code == 200
    response = await client.post("/", form={"prefix-csrf_token": token})
    assert response.status_code == 200
    response = await client.post("/", form={"prefix-csrf_token": ""})
    assert response.status_code == 400
    response = await client.post("/", headers={"X-CSRF-Token": token})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_same_origin(
    app: Quart, client: TestClientProtocol
) -> None:  # pylint: disable=W0621
    """
    Tests same origin.
    """
    await app.startup()
    response = await client.get("/")
    token = response.headers["X-CSRF-Token"]
    headers = {
        "url": "https://localhost",
        "X-CSRF-Token": token
    }
    response = await client.post("/", scheme="https", headers=headers)
    data = await response.get_data(as_text=True)
    assert REFERRER_HEADER in data

    response = await client.post(
        "/",
        scheme="https",
        headers={"X-CSRF-Token": token, "Referer": "http://localhost/"}
    )
    data = await response.get_data(as_text=True)
    assert REFERRER_HOST in data

    response = await client.post(
        "/",
        scheme="https",
        headers={"X-CSRF-Token": token, "Referer": "https://other/"},
    )
    data = await response.get_data(as_text=True)
    assert REFERRER_HOST in data

    response = await client.post(
        "/",
        scheme="https",
        headers={"X-CSRF-Token": token, "Referer": "https://localhost:8080/"},
    )
    data = await response.get_data(as_text=True)
    assert REFERRER_HOST in data

    response = await client.post(
        "/",
        scheme="https",
        headers={"X-CSRF-Token": token, "Referer": "https://localhost/"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_form_csrf_short_circuit(
    app: Quart, client: TestClientProtocol
) -> None:
    """
    Tests CSRF short circuit.
    """
    @app.route("/skip", methods=["POST"])
    async def skip() -> None:
        assert g.get("csrf_valid")
        # don't pass the token, then validate the form
        # this would fail if CSRFProtect didn't run
        form = QuartForm(formdata=None)
        assert await form.validate()

    response = await client.post("/")
    token = response.headers["X-CSRF-Token"]
    response = await client.post("/skip", headers={"X-CSRF-Token": token})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_exempt_view(
    app: Quart, csrf: CSRFProtect, client: TestClientProtocol
) -> None:
    """
    Test exempt view with CSRF.
    """
    @app.route("/exempt", methods=["POST"])
    @csrf.exempt  # typing: ignore
    async def exempt() -> None:
        pass

    response = await client.post("/exempt")
    assert response.status_code == 200

    csrf.exempt("tests.test_csrf_extension.index")
    response = await client.post("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_manual_protect(
    app: Quart, csrf: CSRFProtect, client: TestClientProtocol
) -> None:
    """
    Test manual CSRF protection.
    """
    @app.route("/manual", methods=["GET", "POST"])
    @csrf.exempt  # typing: ignore
    async def manual() -> None:
        await csrf.protect()

    response = await client.get("/manual")
    assert response.status_code == 200

    response = await client.post("/manual")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_exempt_blueprint(
    app: Quart, csrf: CSRFProtect, client: TestClientProtocol
) -> None:
    """
    Test exempting a blueprint from CSRF Protection.
    """
    bp = Blueprint("exempt", __name__, url_prefix="/exempt")
    csrf.exempt(bp)

    @bp.route("/", methods=["POST"])
    async def index() -> None:
        pass

    app.register_blueprint(bp)
    response = await client.post("/exempt/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_error_handler(app: Quart, client: TestClientProtocol) -> None:
    """
    Tests error handling.
    """
    @app.errorhandler(CSRFError)
    async def handle_csrf_error(error: CSRFError) -> str:
        return error.description

    response = await client.post("/")
    assert await response.get_data(as_text=True) == TOKEN_MISSING


@pytest.mark.asyncio
async def test_validate_error_logged(
    client: TestClientProtocol, monkeypatch: Any
) -> None:
    """
    Tests validation error being logged.
    """
    messages = []

    def assert_info(message: List) -> None:
        messages.append(message)

    monkeypatch.setattr(logger, "info", assert_info)

    await client.post("/")
    assert len(messages) == 1
    assert messages[0] == "The CSRF token is missing."  # type: ignore
