"""
Tests the Quart-Form form class.
"""
from io import BytesIO
import pytest

from quart import json, request
from wtforms import FileField, HiddenField, IntegerField, StringField
from wtforms.validators import DataRequired
from wtforms.widgets import HiddenInput

from quart_wtf import QuartForm

class BasicForm(QuartForm):
    class Meta:
        csrf = False

    name = StringField(label='name', validators=[DataRequired()])
    avatar = FileField()

@pytest.mark.asyncio
async def test_populate_from_form(app, client):
    @app.route("/", methods=["POST"])
    async def index():
        form = BasicForm()
        assert form.name.data == "form"

    await client.post("/", data={"name": "form"})

@pytest.mark.asyncio
async def test_populate_from_files(app, client):
    @app.route("/", methods=["POST"])
    async def index():
        form = BasicForm()
        assert form.avatar.data is not None
        assert form.avatar.data.filename == "flask.png"

    await client.post("/", data={"name": "files", "avatar": (BytesIO(), "flask.png")})

@pytest.mark.asyncio
async def test_populate_from_json(app, client):
    @app.route("/", methods=["POST"])
    async def index():
        form = BasicForm()
        assert form.name.data == "json"

    await client.post("/", data=json.dumps({"name": "json"}))

@pytest.mark.asyncio
async def test_populate_manually(app, client):
    @app.route("/", methods=["POST"])
    async def index():
        form = BasicForm(request.args)
        assert form.name.data == "args"

    await client.post("/", query_string={"name": "args"})

@pytest.mark.asyncio
async def test_populate_none(app, client):
    @app.route("/", methods=["POST"])
    async def index():
        form = BasicForm(None)
        assert form.name.data is None

    await client.post("/", data={"name": "ignore"})

@pytest.mark.asyncio
async def test_validate_on_submit(app, client):
    @app.route("/", methods=["POST"])
    async def index():
        form = BasicForm()
        assert form.is_submitted()
        assert not await form.validate_on_submit()
        assert "name" in form.errors

    await client.post("/")

@pytest.mark.asyncio
async def test_no_validate_on_get(app, client):
    @app.route("/", methods=["GET", "POST"])
    async def index():
        form = BasicForm()
        assert not await form.validate_on_submit()
        assert "name" not in form.errors

    await client.get("/")

@pytest.mark.asyncio
async def test_hidden_tag(app):
    class Form(BasicForm):
        class Meta:
            csrf = True

        key = HiddenField()
        count = IntegerField(widget=HiddenInput())

    async with app.test_request_context("/"):
        form = Form()
        out = form.hidden_tag()
        assert all(x in out for x in ("csrf_token", "count", "key"))
        assert "avatar" not in out
        assert "csrf_token" not in form.hidden_tag("count", "key")
