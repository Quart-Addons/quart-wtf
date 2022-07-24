import pytest
import pytest_asyncio
from quart import Quart as _Quart

class Quart(_Quart):
    testing = True
    secret_key = __name__

    async def make_response(self, result):
        if result is None:
            result = ""

        return await super().make_response(result)

@pytest.fixture
def app():
    app = Quart(__name__)
    return app

@pytest_asyncio.fixture
async def app_ctx(app):
    async with app.app_context() as ctx:
        yield ctx

@pytest_asyncio.fixture
async def req_ctx(app):
    async with app.test_request_context() as ctx:
        yield ctx

@pytest_asyncio.fixture
async def client(app):
    return app.test_client()
