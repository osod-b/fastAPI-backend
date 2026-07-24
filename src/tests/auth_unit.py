from fastapi import Cookie
from fastapi.testclient import TestClient
from app.main import app
from app.redis import r_s
import pytest

from schemas.user import UserSchema, UserLogin
from models.user import UserModel

import warnings
warnings.filterwarnings('ignore')

import random
import json

test_client = TestClient(app=app)

def _make_user_model():
        return UserModel

def _make_user_login_schema(username, email, password):
    return UserLogin(username=username, email=email, password=password)

# def _generate_random_user():

def test_user_registration_s1():

    username, email, password = 'primetime', 'primetime@gmail.com', 'primetime1_D_1'
    response = test_client.request(url='/auth/register', method='POST', json={'username': {'value': f'{username}'}, 'email': {'value': f'{email}'}, 'password': {'value': f'{password}'}})
    
    response_data = json.loads(response.content)

    assert response.status_code == 200

# @pytest.mark.skipif()
def test_user_registration_s2():

    immitation_of_code = r_s.get_single_value('user', 'testclient', 'register', 'access_code')
    response = test_client.request(url='/auth/register/verification', method='PATCH', json={'value':f'{immitation_of_code}'})

    response_data = json.loads(response.content)

    assert response.status_code == 200
    assert response_data['message'] == 'Completed'

def test_user_login_s1():
    
    identifier, password, remember_me = 'primetime', 'primetime1_D_1', False

    response = test_client.request(url='/auth/login', method='POST', json={'identifier': {'value': identifier}, 'password': {'value': password}, 'remember_me': remember_me})

    assert response.status_code == 200

    

    

