import pytest
from app.models import User


def assert_user_created(response, user_data):
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert data["username"] == user_data["username"]


def test_register_success(test_client, new_user_data, db_session):
    response = test_client.post("/register", json=new_user_data)
    assert_user_created(response, new_user_data)
    user = db_session.query(User).filter(User.email == new_user_data["email"]).first()
    assert user is not None
    assert user.email == new_user_data["email"]


def test_register_existing_email(test_client, existing_user_data):
    response = test_client.post("/register", json=existing_user_data)
    assert response.status_code == 409
    data = response.json()
    assert "detail" in data
    assert f"User with email {existing_user_data['email']} already exists" in data["detail"]


def test_register_invalid_data(test_client):
    response = test_client.post(
        "/register",
        json={"email": "not-an-email", "password": "short", "username": "deadpool"},
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
