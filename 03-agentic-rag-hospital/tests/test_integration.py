"""Integration tests for the Agentic RAG (Hospital) architecture.

These tests exercise the backend API surface without requiring external
services (Ollama, Qdrant, Elasticsearch) to be running; retrievers and the
LLM client are mocked at the router/agent boundaries.
"""

from unittest.mock import AsyncMock, MagicMock, patch

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


def test_health_and_metrics(client: TestClient) -> None:
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["service"] == "agentic-rag-hospital"

    metrics = client.get("/metrics")
    assert metrics.status_code == 200


def test_full_agent_query_flow(client: TestClient, auth_token: str) -> None:
    mock_result = {
        "query": "What is metformin used for?",
        "answer": "Metformin is used to manage type 2 diabetes.",
        "plan": ["planner step"],
        "reasoning": [
            {"agent": "planner", "step": "created_plan", "detail": {}},
            {"agent": "retriever", "step": "retrieved_sources", "detail": {}},
            {"agent": "verifier", "step": "verified_safety", "detail": {}},
            {"agent": "responder", "step": "generated_answer", "detail": {}},
        ],
        "sources": [
            {"id": "s1", "text": "Metformin overview", "score": 0.95, "metadata": {"patient_id": "pat-001"}, "source": "fusion"},
        ],
        "safety_checks_passed": True,
        "disclaimer": "Medical advice disclaimer appended.",
    }

    with patch("app.routers.query.AgentService") as MockService:
        instance = MockService.return_value
        instance.query = AsyncMock(return_value=MagicMock(**mock_result))

        response = client.post(
            "/api/v1/query/agent",
            json={"query": "What is metformin used for?", "patient_id": "pat-001", "top_k": 3},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "What is metformin used for?"
    assert data["safety_checks_passed"] is True
    assert len(data["reasoning"]) == 4
    assert data["sources"][0]["metadata"]["patient_id"] == "pat-001"


def test_agent_status_endpoint(client: TestClient, auth_token: str) -> None:
    response = client.get(
        "/api/v1/agents/status",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ready"] is True
    assert "planner" in data["agents"]
    assert "retriever" in data["agents"]
    assert "verifier" in data["agents"]
    assert "responder" in data["agents"]


def test_patient_endpoint_integration(client: TestClient, auth_token: str) -> None:
    response = client.get(
        "/api/v1/patients/pat-001",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["patient_id"] == "pat-001"
    assert "Type 2 diabetes mellitus" in data["conditions"]
    assert "Metformin 500mg" in data["medications"]
    assert "Penicillin allergy" in data["allergies"]


def test_guardrail_blocks_pii(client: TestClient, auth_token: str) -> None:
    response = client.post(
        "/api/v1/query/agent",
        json={"query": "My SSN is 123-45-6789, what should I do?"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 400
    assert "pii" in response.json()["detail"]["violations"][0]
