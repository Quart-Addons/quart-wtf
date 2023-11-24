"""
Tests the Quart-Form form class.
"""
from io import BytesIO
import pytest

from quart import Quart, json, request
from quart.typing import TestClientProtocol

from wtforms import FileField, HiddenField, IntegerField, StringField
from wtforms.validators import DataRequired
from wtforms.widgets import HiddenInput

from quart_wtf import QuartForm

class BasicForm(QuartForm):
    """
    Basic test form.
    """
    class Meta:
        """
        Disables CSRF for testing.
        """
        csrf = False

    name = StringField(validators=[DataRequired()])
    avatar = FileField()

@pytest.mark.asyncio
async def test_populate_from_form(app: Quart, client: TestClientProtocol) -> None:
    """
    Populates formdata for the form.
    """
    @app.route("/", methods=["POST"])
    async def index():
        form = await BasicForm().create_form()
        assert form.name.data == "form"

    await client.post("/", form={"name": "form"})

@pytest.mark.asyncio
async def test_populate_from_files(app: Quart, client: TestClientProtocol) -> None:
    """
    Populates formdata for the form using files.
    """
    @app.route("/", methods=["POST"])
    async def index():
        form = await BasicForm().create_form()
        assert form.avatar.data is not None
        assert form.avatar.data.filename == "quart.png"

    await client.post("/", data={"name": "files", "avatar": (BytesIO(), "quart.png")})

@pytest.mark.asyncio
async def test_populate_from_json(app: Quart, client: TestClientProtocol) -> None:
    """
    Populates formdata using json.
    """
    @app.route("/", methods=["POST"])
    async def index():
        form = await BasicForm().create_form()
        assert form.name.data == "json"

    await client.post("/", json=json.dumps({"name": "json"}))

@pytest.mark.asyncio
async def test_populate_manually(app: Quart, client: TestClientProtocol) -> None:
    """
    Manually populates the form.
    """
    @app.route("/", methods=["POST"])
    async def index():
        form = await BasicForm.create_form(fromdata=request.args)
        assert form.name.data == "args"

    await client.post("/", query_string={"name": "args"})

@pytest.mark.asyncio
async def test_populate_none(app: Quart, client: TestClientProtocol) -> None:
    """
    Manually populates the form with no formdata.
    """
    @app.route("/", methods=["POST"])
    async def index():
        form = BasicForm(formdata=None)
        assert form.name.data is None

    await client.post("/", data={"name": "ignore"})

@pytest.mark.asyncio
async def test_validate_on_submit(app: Quart, client: TestClientProtocol) -> None:
    """
    Tests validate on submit for the form.
    """
    @app.route("/", methods=["POST"])
    async def index():
        form = BasicForm()
        assert form.is_submitted()
        assert not await form.validate_on_submit()
        assert "name" in form.errors

    await client.post("/")

@pytest.mark.asyncio
async def test_no_validate_on_get(app: Quart, client: TestClientProtocol) -> None:
    """
    Form not valid on GET requet.
    """
    @app.route("/", methods=["GET", "POST"])
    async def index():
        form = BasicForm()
        assert not await form.validate_on_submit()
        assert "name" not in form.errors

    await client.get("/")

@pytest.mark.asyncio
async def test_hidden_tag(app: Quart) -> None:
    """
    Tests custom hidden tag rendering.
    """
    class Form(BasicForm):
        """
        Form for testing hidden tag.
        """
        class Meta:
            """
            Enables CSRF for testing.
            """
            csrf = True

        key = HiddenField()
        count = IntegerField(widget=HiddenInput())

    async with app.test_request_context("/"):
        form = Form()
        out = form.hidden_tag()
        assert all(x in out for x in ("csrf_token", "count", "key"))
        assert "avatar" not in out
        assert "csrf_token" not in form.hidden_tag("count", "key")
