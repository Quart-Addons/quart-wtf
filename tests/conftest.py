"""
Configures test fixtures.
"""
import pytest
from quart import Quart

@pytest.fixture
def app():
    """
    Returns a Quart app for testing.
    """
    app = Quart(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY=__name__
    )
    return app

@pytest.fixture
def client(app):
    """
    Returns a Quart test client.
    """
    return app.test_client()
