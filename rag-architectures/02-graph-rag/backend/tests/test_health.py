from unittest.mock import patch

import respx
from fastapi.testclient import TestClient
from httpx import Response


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "graph-rag"


@respx.mock
def test_ready(client: TestClient) -> None:
    respx.get("http://localhost:6333/healthz").mock(return_value=Response(200))
    respx.get("http://localhost:11434/api/tags").mock(return_value=Response(200))

    with patch("app.routers.health.GraphRepository.ready", return_value=True):
        response = client.get("/ready")

    assert response.status_code == 200
    data = response.json()
    assert data["ready"] is True
    assert data["checks"]["qdrant"] is True
    assert data["checks"]["neo4j"] is True
    assert data["checks"]["ollama"] is True


def test_metrics(client: TestClient) -> None:
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "graph_rag_requests_total" in response.text
