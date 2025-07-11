"""
tests.recaptcha
"""
from typing import AsyncGenerator, Dict

import pytest
from quart import Quart, json
from quart.ctx import RequestContext
from markupsafe import Markup

from quart_wtf import QuartForm
from quart_wtf.recaptcha import RecaptchaField, recaptcha_before_request


class RecaptchaForm(QuartForm):
    """Recaptcha Test Form"""
    recaptcha = RecaptchaField()


@pytest.fixture
def app(app: Quart) -> Quart:
    """
    Modified test app for testing
    the field
    """
    app.testing = False
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["RECAPTCHA_PUBLIC_KEY"] = "public"
    app.config["RECAPTCHA_PRIVATE_KEY"] = "private"
    recaptcha_before_request(app)
    return app


@pytest.fixture
def resp_data() -> Dict[str, str]:
    """
    Response Data
    """
    return {"g-recaptcha-response": "pass"}


@pytest.mark.asyncio
async def test_config(app: Quart, monkeypatch) -> None:
    """
    Test recaptcha config
    """
    async with app.test_request_context("/", data={"g-recaptcha-response": "pass"}):
        await app.preprocess_request()
        f = await RecaptchaForm.create_form()
        monkeypatch.setattr(app, "testing", True)
        await f.validate()
        assert not f.recaptcha.errors
        monkeypatch.undo()

        monkeypatch.delitem(app.config, "RECAPTCHA_PUBLIC_KEY")
        pytest.raises(RuntimeError, f.recaptcha)
        monkeypatch.undo()

        # monkeypatch.delitem(app.config, "RECAPTCHA_PRIVATE_KEY")
        # with pytest.raises(RuntimeError):
        #     await f.validate()


@pytest.mark.asyncio
async def test_render_has_js(app: Quart) -> None:
    """
    Test that ReCaptcha field renders
    js
    """
    async with app.test_request_context("/"):
        f = RecaptchaForm()
        render = f.recaptcha()
        assert "https://www.google.com/recaptcha/api.js" in render


@pytest.mark.asyncio
async def test_render_custom_js(app: Quart) -> None:
    """
    Test that ReCaptcha field renders
    custom js
    """
    captcha_script = "https://hcaptcha.com/1/api.js"
    app.config["RECAPTCHA_SCRIPT"] = captcha_script

    async with app.test_request_context("/"):
        f = RecaptchaForm()
        render = f.recaptcha()
        assert captcha_script in render


@pytest.mark.asyncio
async def test_render_custom_html(app: Quart) -> None:
    """
    Test rendering of custom html
    """
    app.config["RECAPTCHA_HTML"] = "custom"

    async with app.test_request_context("/"):
        f = RecaptchaForm()
        render = f.recaptcha()
        assert render == "custom"
        assert isinstance(render, Markup)


@pytest.mark.asyncio
async def test_render_custom_div_class(app: Quart) -> None:
    """
    Test rendering a custom div class
    """
    div_class = "h-captcha"
    app.config["RECAPTCHA_DIV_CLASS"] = div_class

    async with app.test_request_context("/"):
        f = RecaptchaForm()
        render = f.recaptcha()
        assert div_class in render


@pytest.mark.asyncio
async def test_render_custom_args(app: Quart) -> None:
    """
    Test rendering custom args
    """
    app.config["RECAPTCHA_PARAMETERS"] = {"key": "(value)"}
    app.config["RECAPTCHA_DATA_ATTRS"] = {"red": "blue"}

    async with app.test_request_context("/"):
        f = RecaptchaForm()
        render = f.recaptcha()
        assert "?key=(value)" in render or "?key=%28value%29" in render
        assert 'data-red="blue"' in render


@pytest.mark.asyncio
async def test_missing_response(
    app: Quart, resp_data: Dict[str, str]
) -> None:
    """
    Test missing response
    """
    async with app.test_request_context("/", method="POST"):
        await app.startup()
        await app.preprocess_request()
        f = RecaptchaForm()
        await f.validate()
        assert f.recaptcha.errors[0] == "The response parameter is missing."
