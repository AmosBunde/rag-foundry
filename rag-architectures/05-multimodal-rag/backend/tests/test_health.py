from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "multimodal-rag"


def test_ready(client: TestClient) -> None:
    with patch("httpx.AsyncClient") as MockClient:
        instance = MockClient.return_value.__aenter__.return_value
        instance.get = MagicMock()
        response_mock = MagicMock()
        response_mock.status_code = 200
        instance.get.return_value = response_mock

        response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert "ready" in data
    assert "checks" in data


def test_metrics(client: TestClient) -> None:
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "multimodal_rag_requests_total" in response.text
