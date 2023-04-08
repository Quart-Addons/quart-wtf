"""
Configures test fixtures.
"""
import pytest
from quart import Quart as _Quart
from quart.typing import TestClientProtocol

class Quart(_Quart):
    """
    Quart Subclass for Testing.
    """
    testing = True
    secret_key = __name__

    async def make_response(self, result):
        if result is None:
            result = ""

        return await super().make_response(result)

@pytest.fixture
def app() -> Quart:
    """
    Returns a Quart app for testing.
    """
    return Quart(__name__)

@pytest.fixture
def client(app: Quart) -> TestClientProtocol:
    """
    Returns a Quart test client.
    """
    return app.test_client()
