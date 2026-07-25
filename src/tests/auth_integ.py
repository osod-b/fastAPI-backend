from httpx import ASGITransport, AsyncClient
from fastapi import Depends
import pytest


from datafaker import testutils, utils, fakedata
from random import randint, randrange
import datafaker
import requests

from app.main import app

from schemas.user import (
    UserRegistration,
    UserLogin,
    )

from validators.users import (
    VerificationalCode, 
    EmailValidator,
    PasswordValidator,
    ) 

@pytest.mark.anyio
async def test_register():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:

        u_rlen = randrange(4, 20)
        p_rlen = randrange(12, 64)
    
        uname = testutils.random_string(u_rlen)
        emal = testutils.random_string(u_rlen) + '@gmail.com'
        pwd = testutils.random_string(p_rlen)
        
        response = ac.post(url='/auth/register', json={
        "username": {
            "value": f"{uname}"
        },
        "email": {
            "value": f'{emal}'
        },
        "password": {
            "value": f'{pwd}'
        }})

        res_data = response.json()

        assert response.status_code == 200
        
        assert res_data["message"] == "Proceed to the next step"
        