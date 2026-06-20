from fastapi.testclient import TestClient


def test_login_success(client: TestClient) -> None:
    response = client.post("/api/v1/auth/token", data={"username": "demo", "password": "demo"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_failure(client: TestClient) -> None:
    response = client.post("/api/v1/auth/token", data={"username": "demo", "password": "wrong"})
    assert response.status_code == 401


def test_protected_endpoint_without_token(client: TestClient) -> None:
    response = client.post("/api/v1/query/multimodal", json={"query": "test"})
    assert response.status_code == 401
