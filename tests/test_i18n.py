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
async def test_i18n(app: Quart, client: TestClientProtocol) -> None:
    """
    Test i18n support for Quart_WTF.
    """
    from quart_babel import Babel

    Babel(app)

    @app.route("/", methods=["POST"])
    async def index() -> None:
        form = await NameForm.create_form()
        await form.validate()

        if not app.config.get("WTF_I18N_ENABLED", True):
            assert form.name.errors[0] == "This field is required."
        elif not form.name.data:
            assert form.name.errors[0] == "该字段是必填字段。"
        else:
            assert form.name.errors[0] == "字段长度必须至少 8 个字符。"

    await client.post("/", headers={"Accept-Language": "zh-CN,zh;q=0.8"})
    await client.post("/", headers={"Accept-Language": "zh"}, data={"name": "short"})
    app.config["WTF_I18N_ENABLED"] = False
    await client.post("/", headers={"Accept-Language": "zh"})
