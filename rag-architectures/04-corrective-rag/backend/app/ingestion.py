from typing import Any

from app.config import settings
from app.models import Document, IngestResponse
from app.retrieval.dense import DenseRetriever
from app.retrieval.sparse import SparseRetriever


def _chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
    """Simple sliding-window chunking."""
    words = text.split()
    if not words:
        return []
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = end - overlap
    return chunks


class IngestionService:
    def __init__(self) -> None:
        self.dense = DenseRetriever()
        self.sparse = SparseRetriever()

    async def ingest(self, documents: list[Document]) -> IngestResponse:
        dense_docs: list[dict[str, Any]] = []
        sparse_docs: list[dict[str, Any]] = []

        for doc in documents:
            chunks = _chunk_text(doc.text)
            if not chunks:
                chunks = [doc.text]
            for idx, chunk in enumerate(chunks):
                chunk_id = f"{doc.id}::chunk::{idx}"
                meta = {**doc.metadata, "parent_id": doc.id, "chunk_index": idx}
                dense_docs.append({"id": chunk_id, "text": chunk, "metadata": meta})
                sparse_docs.append({"id": chunk_id, "text": chunk, "metadata": meta})

        indexed = 0
        errors: list[str] = []

        try:
            indexed += await self.dense.upsert(dense_docs)
        except Exception as exc:  # pragma: no cover
            errors.append(f"Dense index failed: {exc}")

        try:
            indexed += await self.sparse.upsert(sparse_docs)
        except Exception as exc:  # pragma: no cover
            errors.append(f"Sparse index failed: {exc}")

        return IngestResponse(indexed=indexed, errors=errors)
