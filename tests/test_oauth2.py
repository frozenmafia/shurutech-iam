import datetime

import pytest
from app import oauth2
from fastapi import HTTPException


@pytest.fixture
def token_data():
    return {
        "id": 1
    }


def test_create_access_token(token_data):
    access_token = oauth2.create_access_token(token_data)

    decoded_token = oauth2.jwt.decode(access_token, oauth2.SECRET_KEY, oauth2.ALGORITHM)

    assert decoded_token["id"] == token_data["id"]
    expected_expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=oauth2.ACCESS_TOKEN_EXPIRES_MINUTES)
    actual_expire = datetime.datetime.utcfromtimestamp(decoded_token['exp'])
    assert actual_expire - expected_expire < datetime.timedelta(seconds=10)


def test_create_refresh_token(token_data):
    refresh_token = oauth2.create_refresh_token(token_data)
    decoded_token = oauth2.jwt.decode(refresh_token, oauth2.SECRET_KEY, oauth2.ALGORITHM)

    assert decoded_token['id'] == token_data['id']
    expected_expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=oauth2.REFRESH_TOKEN_EXPIRES_MINUTES)
    actual_expire = datetime.datetime.utcfromtimestamp(decoded_token['exp'])
    assert actual_expire - expected_expire < datetime.timedelta(seconds=10)


def test_verify_access_token(token_data):
    token = oauth2.create_access_token(token_data)
    td = oauth2.verify_access_token(token, HTTPException(status_code=401))

    assert td.user_id == str(token_data.get('id'))
