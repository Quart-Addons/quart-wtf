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

    name = StringField(validators=[DataRequired()])
    avatar = FileField()


def test_populate_from_form(app, client):
    @app.route("/", methods=["POST"])
    async def index():
        form = await BasicForm.from_formdata()
        assert form.name.data == "form"

    client.post("/", data={"name": "form"})


def test_populate_from_files(app, client):
    @app.route("/", methods=["POST"])
    async def index():
        form = await BasicForm.from_formdata()
        assert form.avatar.data is not None
        assert form.avatar.data.filename == "flask.png"

    client.post("/", data={"name": "files", "avatar": (BytesIO(), "flask.png")})


def test_populate_from_json(app, client):
    @app.route("/", methods=["POST"])
    async def index():
        form = await BasicForm.from_formdata()
        assert form.name.data == "json"

    client.post("/", data=json.dumps({"name": "json"}), content_type="application/json")


def test_populate_manually(app, client):
    @app.route("/", methods=["POST"])
    async def index():
        form = BasicForm(request.args)
        assert form.name.data == "args"

    client.post("/", query_string={"name": "args"})


def test_populate_none(app, client):
    @app.route("/", methods=["POST"])
    async def index():
        form = BasicForm(None)
        assert form.name.data is None

    client.post("/", data={"name": "ignore"})


def test_validate_on_submit(app, client):
    @app.route("/", methods=["POST"])
    async def index():
        form = await BasicForm.from_formdata()
        assert form.is_submitted()
        assert not form.validate_on_submit()
        assert "name" in form.errors

    client.post("/")


def test_no_validate_on_get(app, client):
    @app.route("/", methods=["GET", "POST"])
    async def index():
        form = await BasicForm.from_formdata()
        assert not form.validate_on_submit()
        assert "name" not in form.errors

    client.get("/")

@pytest.mark.asyncio
async def test_hidden_tag(req_ctx):
    class Form(BasicForm):
        class Meta:
            csrf = True

        key = HiddenField()
        count = IntegerField(widget=HiddenInput())

    form = await Form.from_formdata()
    out = form.hidden_tag()
    assert all(x in out for x in ("csrf_token", "count", "key"))
    assert "avatar" not in out
    assert "csrf_token" not in form.hidden_tag("count", "key")
