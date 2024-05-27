import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_home(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello world"}
