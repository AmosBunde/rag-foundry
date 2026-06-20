from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


def test_ingest_text_success(client: TestClient, auth_token: str) -> None:
    with patch("app.ingestion.MultimodalRetriever") as MockRetriever:
        MockRetriever.return_value.upsert = AsyncMock(return_value=2)

        response = client.post(
            "/api/v1/ingest/text",
            json={
                "documents": [
                    {"id": "doc-1", "text": "Multimodal RAG supports text, images, and audio.", "metadata": {"source": "wiki"}},
                ]
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["indexed"] == 2


def test_ingest_text_validation_error(client: TestClient, auth_token: str) -> None:
    response = client.post(
        "/api/v1/ingest/text",
        json={"documents": []},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 422


def test_ingest_image_success(client: TestClient, auth_token: str) -> None:
    with patch("app.ingestion.MultimodalRetriever") as MockRetriever, \
         patch("app.ingestion.LLMClient") as MockLLM:
        MockRetriever.return_value.upsert = AsyncMock(return_value=1)
        MockLLM.return_value.caption_image = AsyncMock(return_value="A test image")

        response = client.post(
            "/api/v1/ingest/image",
            files={"file": ("test.png", b"fake-image", "image/png")},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "indexed"
    assert data["caption"] == "A test image"


def test_ingest_image_unsupported_type(client: TestClient, auth_token: str) -> None:
    response = client.post(
        "/api/v1/ingest/image",
        files={"file": ("test.gif", b"fake-image", "image/gif")},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 415


def test_ingest_audio_success(client: TestClient, auth_token: str) -> None:
    with patch("app.ingestion.MultimodalRetriever") as MockRetriever, \
         patch("app.ingestion.LLMClient") as MockLLM:
        MockRetriever.return_value.upsert = AsyncMock(return_value=2)
        MockLLM.return_value.transcribe_audio = AsyncMock(return_value="Hello world")

        response = client.post(
            "/api/v1/ingest/audio",
            files={"file": ("test.mp3", b"fake-audio", "audio/mpeg")},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "indexed"
    assert data["transcription"] == "Hello world"


def test_ingest_audio_unsupported_type(client: TestClient, auth_token: str) -> None:
    response = client.post(
        "/api/v1/ingest/audio",
        files={"file": ("test.ogg", b"fake-audio", "audio/ogg")},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 415
