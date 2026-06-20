"""Integration tests for Hybrid RAG.

These tests mock external services (Qdrant, Elasticsearch, Ollama) and verify
end-to-end API flows.
"""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.models import RetrievedChunk


@pytest.fixture
def client() -> TestClient:
    from app.main import app
    return TestClient(app)


@pytest.fixture
def auth_token(client: TestClient) -> str:
    response = client.post("/api/v1/auth/token", data={"username": "demo", "password": "demo"})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_full_ingest_and_query_flow(client: TestClient, auth_token: str) -> None:
    with patch("app.ingestion.DenseRetriever") as MockDense, \
         patch("app.ingestion.SparseRetriever") as MockSparse:
        MockDense.return_value.upsert = AsyncMock(return_value=2)
        MockSparse.return_value.upsert = AsyncMock(return_value=2)

        ingest_response = client.post(
            "/api/v1/ingest",
            json={
                "documents": [
                    {"id": "doc-1", "text": "Hybrid RAG combines dense and sparse retrieval.", "metadata": {"source": "test"}},
                ]
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert ingest_response.status_code == 200
        assert ingest_response.json()["indexed"] == 4

    with patch("app.routers.query.DenseRetriever") as MockDense, \
         patch("app.routers.query.SparseRetriever") as MockSparse:
        MockDense.return_value.search = AsyncMock(return_value=[
            RetrievedChunk(id="d1", text="dense result", score=0.9, metadata={}, source="dense"),
        ])
        MockSparse.return_value.search = AsyncMock(return_value=[
            RetrievedChunk(id="s1", text="sparse result", score=0.8, metadata={}, source="sparse"),
        ])

        query_response = client.post(
            "/api/v1/query/hybrid",
            json={"query": "What is hybrid RAG?", "top_k": 2},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert query_response.status_code == 200
        data = query_response.json()
        assert data["query"] == "What is hybrid RAG?"
        assert len(data["results"]) <= 2
