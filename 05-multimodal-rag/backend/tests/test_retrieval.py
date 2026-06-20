from unittest.mock import MagicMock, patch

import pytest
import respx
from httpx import Response

from app.retrieval.multimodal import MultimodalRetriever


@pytest.mark.asyncio
@respx.mock
async def test_multimodal_search() -> None:
    with patch("app.retrieval.multimodal.QdrantClient") as MockClient:
        instance = MockClient.return_value
        instance.collection_exists.return_value = True
        instance.search.return_value = [
            MagicMock(id="x", score=0.95, payload={"modality": "text", "content": "found", "metadata": {}})
        ]

        retriever = MultimodalRetriever()
        respx.post(f"{retriever.embedder.ollama_url}/api/embeddings").mock(
            return_value=Response(200, json={"embedding": [0.1] * 512})
        )

        results = await retriever.search("query", top_k=1, modalities=["text"])
        assert len(results) == 1
        assert results[0].id == "x"
        assert results[0].modality == "text"


@pytest.mark.asyncio
async def test_multimodal_upsert() -> None:
    with patch("app.retrieval.multimodal.QdrantClient") as MockClient:
        instance = MockClient.return_value
        instance.collection_exists.return_value = True

        retriever = MultimodalRetriever()
        with patch.object(retriever.embedder, "embed_modality", return_value=[[0.1] * 512]):
            count = await retriever.upsert(
                [{"id": "1", "modality": "text", "content": "hello", "metadata": {}}]
            )
        assert count == 1
        instance.upsert.assert_called_once()
