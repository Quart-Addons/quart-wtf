"""
Test i18n support.
"""
import pytest

from quart import Quart, request
from quart.typing import TestClientProtocol
from wtforms import StringField
from wtforms.validators import DataRequired, Length

from quart_wtf import QuartForm

#pytest.importorskip("quart_wtf.i18n", reason="Quart-Babel is not installed.")

class NameForm(QuartForm):
    """
    The name form to use for testing
    i18n support.
    """
    class Meta:
        """
        Override meta class.
        """
        csrf = False

    name = StringField(validators=[DataRequired(), Length(min=8)])

@pytest.mark.asyncio
async def test_no_extension(app: Quart, client: TestClientProtocol) -> None:
    """
    Test that there is no babel extension.
    """
    @app.route("/", methods=["POST"])
    async def index():
        """
        Test route for the test.
        """
        form = NameForm()
        await form.validate()
        assert form.name.errors[0] == "This field is required."

    await client.post("/", headers={"Accept-Language": "zh-CN,zh;q=0.8"})

@pytest.mark.asyncio
async def test_outside_request():
    """
    Test when there is no request.
    """
    pytest.importorskip("babel")
    from quart_wtf.i18n import translations

    s = "This field is requred."
    assert translations.gettext(s) == s