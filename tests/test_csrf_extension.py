"""
Tests the CSRF extension from Quart-WTF.
"""
import pytest
from quart import Blueprint, g, render_template_string

from quart_wtf.csrf import CSRFError, CSRFProtect, generate_csrf
from quart_wtf.form import QuartForm

@pytest.fixture
def app(app):
    CSRFProtect(app)

    @app.route("/", methods=["GET", "POST"])
    async def index():
        pass

    @app.after_request
    async def add_csrf_header(response):
        response.headers.set("X-CSRF-Token", generate_csrf())
        return response

    return app


@pytest.fixture
def csrf(app):
    return app.extensions["csrf"]

@pytest.mark.asyncio
async def test_render_token(req_ctx):
    token = generate_csrf()
    assert await render_template_string("{{ csrf_token() }}") == token

@pytest.mark.asyncio
async def test_protect(app, client, app_ctx):
    response = await client.post("/")
    assert response.status_code == 400
    assert "The CSRF token is missing." in response.get_data(as_text=True)

    app.config["WTF_CSRF_ENABLED"] = False
    assert await client.post("/").get_data() == b""
    app.config["WTF_CSRF_ENABLED"] = True

    app.config["WTF_CSRF_CHECK_DEFAULT"] = False
    assert await client.post("/").get_data() == b""
    app.config["WTF_CSRF_CHECK_DEFAULT"] = True

    assert await client.options("/").status_code == 200
    assert await client.post("/not-found").status_code == 404

    response = await client.get("/")
    assert response.status_code == 200
    token = response.headers["X-CSRF-Token"]
    assert await client.post("/", data={"csrf_token": token}).status_code == 200
    assert await client.post("/", data={"prefix-csrf_token": token}).status_code == 200
    assert await client.post("/", data={"prefix-csrf_token": ""}).status_code == 400
    assert await client.post("/", headers={"X-CSRF-Token": token}).status_code == 200

@pytest.mark.asyncio
async def test_same_origin(client):
    token = await client.get("/").headers["X-CSRF-Token"]
    response = await client.post(
        "/", base_url="https://localhost", headers={"X-CSRF-Token": token}
    )
    data = response.get_data(as_text=True)
    assert "The referrer header is missing." in data

    response = await client.post(
        "/",
        base_url="https://localhost",
        headers={"X-CSRF-Token": token, "Referer": "http://localhost/"},
    )
    data = response.get_data(as_text=True)
    assert "The referrer does not match the host." in data

    response = await client.post(
        "/",
        base_url="https://localhost",
        headers={"X-CSRF-Token": token, "Referer": "https://other/"},
    )
    data = response.get_data(as_text=True)
    assert "The referrer does not match the host." in data

    response = await client.post(
        "/",
        base_url="https://localhost",
        headers={"X-CSRF-Token": token, "Referer": "https://localhost:8080/"},
    )
    data = response.get_data(as_text=True)
    assert "The referrer does not match the host." in data

    response = await client.post(
        "/",
        base_url="https://localhost",
        headers={"X-CSRF-Token": token, "Referer": "https://localhost/"},
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_form_csrf_short_circuit(app, client):
    @app.route("/skip", methods=["POST"])
    async def skip():
        assert g.get("csrf_valid")
        # don't pass the token, then validate the form
        # this would fail if CSRFProtect didn't run
        form = QuartForm(None)
        assert form.validate()

    token = await client.get("/").headers["X-CSRF-Token"]
    response = await client.post("/skip", headers={"X-CSRF-Token": token})
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_exempt_view(app, csrf, client):
    @app.route("/exempt", methods=["POST"])
    @csrf.exempt
    async def exempt():
        pass

    response = await client.post("/exempt")
    assert response.status_code == 200

    csrf.exempt("test_csrf_extension.index")
    response = await client.post("/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_manual_protect(app, csrf, client):
    @app.route("/manual", methods=["GET", "POST"])
    @csrf.exempt
    async def manual():
        csrf.protect()

    response = await client.get("/manual")
    assert response.status_code == 200

    response = await client.post("/manual")
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_exempt_blueprint(app, csrf, client):
    bp = Blueprint("exempt", __name__, url_prefix="/exempt")
    csrf.exempt(bp)

    @bp.route("/", methods=["POST"])
    async def index():
        pass

    app.register_blueprint(bp)
    response = await client.post("/exempt/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_error_handler(app, client):
    @app.errorhandler(CSRFError)
    async def handle_csrf_error(e):
        return e.description.lower()

    response = await client.post("/")
    assert response.get_data(as_text=True) == "the csrf token is missing."

@pytest.mark.asyncio
async def test_validate_error_logged(client, monkeypatch):
    from quart_wtf.csrf import logger

    messages = []

    def assert_info(message):
        messages.append(message)

    monkeypatch.setattr(logger, "info", assert_info)

    await client.post("/")
    assert len(messages) == 1
    assert messages[0] == "The CSRF token is missing."
