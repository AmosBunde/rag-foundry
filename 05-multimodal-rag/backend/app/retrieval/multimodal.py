import logging
import uuid
from typing import Any

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, Filter, FieldCondition, MatchValue, PointStruct, VectorParams

from app.config import settings
from app.embedding import EmbeddingService
from app.models import Modality, MultimodalResult


class MultimodalRetriever:
    """Dense retrieval over text, image, and audio embeddings in a single Qdrant collection."""

    def __init__(self) -> None:
        self.client = QdrantClient(url=settings.qdrant_url)
        self.collection = settings.multimodal_collection
        self.vector_size = settings.vector_size
        self.embedder = EmbeddingService()
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        try:
            if not self.client.collection_exists(self.collection):
                self.client.create_collection(
                    collection_name=self.collection,
                    vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
                )
        except Exception as exc:  # pragma: no cover
            logger = logging.getLogger(__name__)
            logger.warning("Could not ensure Qdrant collection %s: %s", self.collection, exc)

    async def upsert(
        self,
        items: list[dict[str, Any]],
    ) -> int:
        """Upsert multimodal items. Each item must have id, modality, content, and optional metadata."""
        if not items:
            return 0

        by_modality: dict[Modality, list[tuple[dict[str, Any], Any]]] = {"text": [], "image": [], "audio": []}
        for item in items:
            modality = item["modality"]
            if modality in by_modality:
                by_modality[modality].append((item, item["content"]))

        embeddings: dict[int, list[float]] = {}
        item_index = 0
        for modality, pairs in by_modality.items():
            if not pairs:
                continue
            payloads = [p[1] for p in pairs]
            modality_embeddings = await self.embedder.embed_modality(modality, payloads)
            for idx, embedding in enumerate(modality_embeddings):
                embeddings[item_index + idx] = embedding
            item_index += len(pairs)

        points = []
        for idx, item in enumerate(items):
            point_id = item.get("id") or str(uuid.uuid4())
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embeddings[idx],
                    payload={
                        "modality": item["modality"],
                        "content": str(item["content"])[:10_000],
                        "metadata": item.get("metadata", {}),
                    },
                )
            )

        self.client.upsert(collection_name=self.collection, points=points)
        return len(points)

    async def search(
        self,
        query: str,
        top_k: int = 5,
        modalities: list[Modality] | None = None,
    ) -> list[MultimodalResult]:
        vectors = await self.embedder.embed_text([query])
        vector = np.array(vectors[0]).tolist()

        search_filter = None
        if modalities:
            search_filter = Filter(
                should=[FieldCondition(key="modality", match=MatchValue(value=m)) for m in modalities]
            )

        results = self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            limit=top_k,
            with_payload=True,
            query_filter=search_filter,
        )
        return [
            MultimodalResult(
                id=str(r.id),
                modality=r.payload.get("modality", "text"),
                content=r.payload.get("content", ""),
                score=float(r.score),
                metadata=r.payload.get("metadata", {}),
            )
            for r in results
        ]
