"""
Configures test fixtures.
"""
import pytest
from quart import Quart as _Quart
from quart.typing import ResponseReturnValue, ResponseTypes, TestClientProtocol
from werkzeug.exceptions import HTTPException


class Quart(_Quart):
    """
    Subclass of Quart for test Quart-WTF.
    """
    async def make_response(
            self, result: ResponseReturnValue | HTTPException
    ) -> ResponseTypes:
        """
        Overload meth to make sure the result is never ``None``.
        """
        if result is None:
            result = ""
        return await super().make_response(result)


@pytest.fixture
def app() -> Quart:
    """
    Returns a Quart app for testing.
    """
    app = Quart(__name__)
    app.config['SECRET_KEY'] = __name__
    return app


@pytest.fixture
def client(app: Quart) -> TestClientProtocol:
    """
    Returns a Quart test client.
    """
    return app.test_client()
