import uuid
from typing import Any

import httpx
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from app.config import settings
from app.llm import LLMClient
from app.models import RetrievedChunk


class DenseRetriever:
    """Dense retrieval using Qdrant and a local embedding model via Ollama."""

    def __init__(self) -> None:
        self.client = QdrantClient(url=settings.qdrant_url)
        self.collection = settings.dense_collection
        self.llm = LLMClient()
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE),
            )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings via Ollama embeddings API."""
        if not texts:
            return []
        return await self.llm.embed(texts)

    async def upsert(self, documents: list[dict[str, Any]]) -> int:
        texts = [doc["text"] for doc in documents]
        embeddings = await self.embed(texts)
        points = []
        for doc, vector in zip(documents, embeddings):
            point_id = doc.get("id") or str(uuid.uuid4())
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={"text": doc["text"], "metadata": doc.get("metadata", {})},
                )
            )
        self.client.upsert(collection_name=self.collection, points=points)
        return len(points)

    async def search(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        vectors = await self.embed([query])
        vector = np.array(vectors[0]).tolist()
        results = self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            limit=top_k,
            with_payload=True,
        )
        return [
            RetrievedChunk(
                id=str(r.id),
                text=r.payload.get("text", ""),
                score=float(r.score),
                metadata=r.payload.get("metadata", {}),
                source="dense",
            )
            for r in results
        ]
