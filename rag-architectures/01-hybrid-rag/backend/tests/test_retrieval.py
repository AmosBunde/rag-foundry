from unittest.mock import MagicMock, patch

import pytest
import respx
from httpx import Response

from app.retrieval.dense import DenseRetriever
from app.retrieval.sparse import SparseRetriever


@pytest.mark.asyncio
@respx.mock
async def test_dense_search() -> None:
    with patch("app.retrieval.dense.QdrantClient") as MockClient:
        instance = MockClient.return_value
        instance.collection_exists.return_value = True
        instance.search.return_value = [
            MagicMock(id="x", score=0.95, payload={"text": "found", "metadata": {}})
        ]

        retriever = DenseRetriever()
        respx.post(f"{retriever.ollama_url}/api/embeddings").mock(
            return_value=Response(200, json={"embedding": [0.1] * 768})
        )

        results = await retriever.search("query", top_k=1)
        assert len(results) == 1
        assert results[0].id == "x"


@pytest.mark.asyncio
async def test_sparse_search() -> None:
    with patch("app.retrieval.sparse.Elasticsearch") as MockEs:
        instance = MockEs.return_value
        instance.indices.exists.return_value = True
        instance.search.return_value = {
            "hits": {
                "max_score": 1.0,
                "hits": [
                    {"_id": "y", "_score": 0.8, "_source": {"text": "found", "metadata": {}}}
                ],
            }
        }
        retriever = SparseRetriever()
        results = await retriever.search("query", top_k=1)
        assert len(results) == 1
        assert results[0].id == "y"
