import numpy as np
import pytest
import respx
from httpx import Response

from app.embedding import EmbeddingService


def test_mock_vector_deterministic() -> None:
    from app.embedding import _mock_vector

    v1 = _mock_vector("hello", 512)
    v2 = _mock_vector("hello", 512)
    assert v1 == v2
    assert len(v1) == 512
    assert abs(np.linalg.norm(v1) - 1.0) < 1e-6


@pytest.mark.asyncio
async def test_embed_text_mock_mode() -> None:
    service = EmbeddingService()
    service.mock_mode = True
    result = await service.embed_text(["hello", "world"])
    assert len(result) == 2
    assert len(result[0]) == service.vector_size


@pytest.mark.asyncio
@respx.mock
async def test_embed_text_ollama_fallback() -> None:
    service = EmbeddingService()
    service.mock_mode = False
    respx.post(f"{service.ollama_url}/api/embeddings").mock(
        return_value=Response(500, json={"error": "boom"})
    )

    result = await service.embed_text(["hello"])
    assert len(result) == 1
    assert len(result[0]) == service.vector_size


@pytest.mark.asyncio
async def test_embed_image_and_audio() -> None:
    service = EmbeddingService()
    service.mock_mode = True
    img = await service.embed_image([b"img"])
    audio = await service.embed_audio([b"audio"])
    assert len(img) == 1
    assert len(audio) == 1
    assert len(img[0]) == service.vector_size
    assert len(audio[0]) == service.vector_size
