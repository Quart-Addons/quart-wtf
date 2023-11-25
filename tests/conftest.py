"""
Configures test fixtures.
"""
import pytest
from quart import Quart
from quart.typing import TestClientProtocol

@pytest.fixture
def app() -> Quart:
    """
    Returns a Quart app for testing.
    """
    app = Quart(__name__)
    app.secret_key = __name__
    return app

@pytest.fixture
def client(app: Quart) -> TestClientProtocol:
    """
    Returns a Quart test client.
    """
    return app.test_client()
