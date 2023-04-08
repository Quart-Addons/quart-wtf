"""
Test i18n support.
"""
import pytest
from quart import Quart
from quart.typing import TestClientProtocol
from wtforms import StringField
from wtforms.validators import DataRequired, Length

from quart_wtf import QuartForm

pytest.importorskip("quart_wtf.i18n", reason="Quart-Babel is not installed.")

class NameForm(QuartForm):
    """
    Name Form.
    """
    name = StringField(validators=[DataRequired(), Length(min=8)])

@pytest.mark.asyncio
async def test_no_extension(app: Quart, client: TestClientProtocol) -> None:
    """
    Test that there is no babel extension installed.
    """
    @app.route("/", methods=["POST"])
    async def index():
        form = NameForm()
        await form.validate()
        assert form.name.errors[0] == "This field is required."

    await client.post("/", headers={"Accept-Language": "zh-CN,zh;q=0.8"})
