import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def auth_token(client: TestClient) -> str:
    response = client.post("/api/v1/auth/token", data={"username": "demo", "password": "demo"})
    assert response.status_code == 200
    return response.json()["access_token"]
