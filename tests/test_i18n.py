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
    class Meta:
        csrf = False

    name = StringField(validators=[DataRequired(), Length(min=8)])

@pytest.mark.asyncio
async def test_no_extension(app: Quart, client: TestClientProtocol) -> None:
    """
    Test that there is no babel extension.
    """
    @app.route("/", methods=["POST"])
    async def index():
        form = NameForm()
        await form.validate()
        assert form.name.errors[0] == "This field is required."

    await client.post("/", headers={"Accept-Language": "zh-CN,zh;q=0.8"})

@pytest.mark.asyncio
async def test_i18n(app: Quart, client: TestClientProtocol) -> None:
    """
    Test i18n support for forms.
    """
    try:
        from quart_babel import Babel, select_locale_by_request
        from quart_babel.typing import ASGIRequest
    except ImportError:
        pytest.skip("Quart-Babel must be installed")

    Babel(app)

    @app.route("/", methods=["POST"])
    async def index():
        form = NameForm()
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
