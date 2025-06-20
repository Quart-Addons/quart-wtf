"""
tests.recaptcha
"""
from typing import Dict

import pytest
from quart import Quart, json
from markupsafe import Markup

from quart_wtf import QuartForm
from quart_wtf.recaptcha import RecaptchaField, recaptcha_validation


class RecaptchaForm(QuartForm):
    """Recaptcha Test Form"""
    class Meta:
        crsf = False

    recaptcha = RecaptchaField()

    async def async_validator_recaptcha(self, field) -> None:
        """Custom recaptch validator"""
        return await recaptcha_validation(field)


@pytest.fixture
def app(app: Quart) -> Quart:
    """
    Modified test app for testing
    the field
    """
    app.testing = False
    app.config["RECAPTCHA_PUBLIC_KEY"] = "public"
    app.config["RECAPTCHA_PRIVATE_KEY"] = "private"
    return app


@pytest.fixture
def req_data() -> Dict[str, str]:
    """
    Data for the request
    """
    return {"g-recaptcha-response": "pass"}


@pytest.mark.asyncio
async def test_config(app: Quart, req_data: Dict[str, str], monkeypatch) -> None:
    """
    Test Recaptcha Config
    """
    async with app.test_request_context("/", method="POST", data=req_data):
        form = await RecaptchaForm.create_form()
        monkeypatch.setattr(app, "testing", True)
        await form.validate()
        assert not form.recaptcha.errors
        monkeypatch.undo()

        monkeypatch.delitem(app.config, "RECAPTCHA_PUBLIC_KEY")
        pytest.raises(RuntimeError, form.recaptcha)
        monkeypatch.undo()

        # monkeypatch.delitem(app.config, "RECAPTCHA_PRIVATE_KEY")
        # pytest.raises(RuntimeError, form.validate)


@pytest.mark.asyncio
async def test_render_has_js(app: Quart, req_data: Dict[str, str]) -> None:
    """
    Test render has js
    """
    async with app.test_request_context("/", method="GET"):
        form = RecaptchaForm()
        render = form.recaptcha()
        assert "https://www.google.com/recaptcha/api.js" in render


@pytest.mark.asyncio
async def test_render_has_custom_js(app: Quart) -> None:
    """
    Test render has custom js
    """
    captcha_script = "https://hcaptcha.com/1/api.js"
    app.config["RECAPTCHA_SCRIPT"] = captcha_script
    async with app.test_request_context("/", method="GET"):
        form = RecaptchaForm()
        render = form.recaptcha()
        assert captcha_script in render


@pytest.mark.asyncio
async def test_render_custom_div_class(app: Quart) -> None:
    """
    Test custom div class
    """
    div_class = "h-captcha"
    app.config["RECAPTCHA_DIV_CLASS"] = div_class

    async with app.test_request_context("/", method="GET"):
        form = RecaptchaForm()
        render = form.recaptcha()
        assert div_class in render


@pytest.mark.asyncio
async def test_render_custom_args(app: Quart) -> None:
    """
    Test custom args
    """
    app.config["RECAPTCHA_PARAMETERS"] = {"key": "(value)"}
    app.config["RECAPTCHA_DATA_ATTRS"] = {"red": "blue"}

    async with app.test_request_context("/", method="GET"):
        form = RecaptchaForm()
        render = form.recaptcha()
        assert "?key=(value)" in render or "?key=%28value%29" in render
        assert 'data-red="blue"' in render


@pytest.mark.asyncio
async def test_missing_response(app: Quart) -> None:
    """
    Test missing response
    """
    async with app.test_request_context("/", method="GET"):
        form = await RecaptchaForm.create_form()
        await form.validate()
        assert form.recaptcha.errors[0] == "The response parameter is missing."
        # print(form.recaptcha.errors)
