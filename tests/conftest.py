import pytest
import pytest_asyncio
from quart import Quart

@pytest.fixture
def app():
    app = Quart(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY=__name__
    )
    return app

@pytest_asyncio.fixture
async def app_ctx(app):
    async with app.app_context() as ctx:
        yield ctx

@pytest_asyncio.fixture
async def req_ctx(app):
    async with app.test_request_context("/") as ctx:
        yield ctx

@pytest.fixture
def client(app):
    return app.test_client()
