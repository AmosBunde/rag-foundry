from typing import Any

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from app.config import settings
from app.models import RetrievedChunk


class SparseRetriever:
    """Sparse retrieval using Elasticsearch BM25."""

    def __init__(self) -> None:
        self.client = Elasticsearch(settings.elasticsearch_url)
        self.index = settings.sparse_index
        self._ensure_index()

    def _ensure_index(self) -> None:
        if not self.client.indices.exists(index=self.index):
            self.client.indices.create(
                index=self.index,
                body={
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 0,
                        "analysis": {
                            "analyzer": {
                                "default": {
                                    "type": "standard",
                                }
                            }
                        },
                    },
                    "mappings": {
                        "properties": {
                            "text": {"type": "text"},
                            "metadata": {"type": "object", "dynamic": True},
                        }
                    },
                },
            )

    async def upsert(self, documents: list[dict[str, Any]]) -> int:
        actions = []
        for doc in documents:
            actions.append(
                {
                    "_index": self.index,
                    "_id": doc.get("id"),
                    "_source": {
                        "text": doc["text"],
                        "metadata": doc.get("metadata", {}),
                    },
                }
            )
        success, _ = bulk(self.client, actions, refresh=True)
        return success

    async def search(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        response = self.client.search(
            index=self.index,
            body={
                "query": {"match": {"text": query}},
                "size": top_k,
            },
        )
        hits = response.get("hits", {}).get("hits", [])
        max_score = response.get("hits", {}).get("max_score") or 1.0
        return [
            RetrievedChunk(
                id=str(h["_id"]),
                text=h["_source"].get("text", ""),
                score=(h["_score"] or 0.0) / max_score,
                metadata=h["_source"].get("metadata", {}),
                source="sparse",
            )
            for h in hits
        ]
