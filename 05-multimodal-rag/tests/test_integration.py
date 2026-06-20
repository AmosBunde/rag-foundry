"""Integration tests for the Multi-Modal RAG backend.

These tests exercise the full request/response flow through the FastAPI app
using mocked external services (Qdrant, Ollama, Redis).
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def token(client: TestClient) -> str:
    response = client.post("/api/v1/auth/token", data={"username": "demo", "password": "demo"})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_full_text_ingest_and_query_flow(client: TestClient, token: str) -> None:
    with patch("app.ingestion.MultimodalRetriever") as MockRetriever:
        instance = MockRetriever.return_value
        instance.upsert = AsyncMock(return_value=2)

        ingest_response = client.post(
            "/api/v1/ingest/text",
            json={"documents": [{"id": "doc-1", "text": "Multi-modal retrieval supports text, images, and audio.", "metadata": {"source": "test"}}]},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert ingest_response.status_code == 200
        assert ingest_response.json()["indexed"] == 2

    with patch("app.routers.query.MultimodalRetriever") as MockRetriever:
        instance = MockRetriever.return_value
        instance.search = AsyncMock(return_value=[
            {"id": "doc-1::chunk::0", "modality": "text", "content": "Multi-modal retrieval supports text", "score": 0.95, "metadata": {"source": "test"}}
        ])

        query_response = client.post(
            "/api/v1/query/multimodal",
            json={"query": "multi-modal retrieval", "top_k": 3},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert query_response.status_code == 200
        data = query_response.json()
        assert data["query"] == "multi-modal retrieval"
        assert len(data["results"]) == 1
        assert data["results"][0]["modality"] == "text"


def test_image_upload_flow(client: TestClient, token: str) -> None:
    with patch("app.ingestion.MultimodalRetriever") as MockRetriever, \
         patch("app.ingestion.LLMClient") as MockLLM:
        MockRetriever.return_value.upsert = AsyncMock(return_value=1)
        MockLLM.return_value.caption_image = AsyncMock(return_value="A test image")

        response = client.post(
            "/api/v1/ingest/image",
            files={"file": ("test.png", b"fake-image", "image/png")},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "indexed"


def test_audio_upload_flow(client: TestClient, token: str) -> None:
    with patch("app.ingestion.MultimodalRetriever") as MockRetriever, \
         patch("app.ingestion.LLMClient") as MockLLM:
        MockRetriever.return_value.upsert = AsyncMock(return_value=2)
        MockLLM.return_value.transcribe_audio = AsyncMock(return_value="Hello world")

        response = client.post(
            "/api/v1/ingest/audio",
            files={"file": ("test.mp3", b"fake-audio", "audio/mpeg")},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "indexed"


def test_query_modalities_filter(client: TestClient, token: str) -> None:
    with patch("app.routers.query.MultimodalRetriever") as MockRetriever:
        instance = MockRetriever.return_value
        instance.search = AsyncMock(return_value=[])

        response = client.post(
            "/api/v1/query/multimodal",
            json={"query": "example", "top_k": 5, "modalities": ["image", "audio"]},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["modalities"] == ["image", "audio"]
