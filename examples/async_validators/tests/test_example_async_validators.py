"""
Test async validator example.
"""
from async_validators import app 

async def test_login():
    test_client = app.test_client()
    form = {
        "username": "username", 
        "password": "testpwd", 
        "password_confirm": "testpwd"
    }
    response = await test_client.post("/", form=form)
    assert response.status_code == 302
    #response = await response.get_data()
