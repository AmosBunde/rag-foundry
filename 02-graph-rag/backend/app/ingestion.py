from typing import Any

from app.config import settings
from app.graph import GraphRepository, build_relationships, extract_entities
from app.models import Document, IngestResponse
from app.retrieval.dense import DenseRetriever


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
        self.graph = GraphRepository()

    async def ingest(self, documents: list[Document]) -> IngestResponse:
        all_dense_docs: list[dict[str, Any]] = []
        all_entities: list[dict[str, Any]] = []
        all_relationships: list[dict[str, Any]] = []
        all_chunks: list[dict[str, Any]] = []

        for doc in documents:
            chunks = _chunk_text(doc.text)
            if not chunks:
                chunks = [doc.text]
            for idx, chunk_text in enumerate(chunks):
                chunk_id = f"{doc.id}::chunk::{idx}"
                meta = {**doc.metadata, "parent_id": doc.id, "chunk_index": idx}
                all_dense_docs.append({"id": chunk_id, "text": chunk_text, "metadata": meta})
                all_chunks.append({"id": chunk_id, "text": chunk_text, "parent_id": doc.id, "chunk_index": idx})

                entities = extract_entities(
                    chunk_text,
                    chunk_id=chunk_id,
                    max_entities=settings.max_entities_per_chunk,
                )
                all_entities.extend(entities)
                all_relationships.extend(build_relationships(entities, chunk_id))

        indexed = 0
        entities_created = 0
        relationships_created = 0
        errors: list[str] = []

        try:
            indexed += await self.dense.upsert(all_dense_docs)
        except Exception as exc:
            errors.append(f"Dense index failed: {exc}")

        try:
            for doc in documents:
                doc_chunks = [c for c in all_chunks if c["parent_id"] == doc.id]
                doc_entities = [e for e in all_entities if e["chunk_id"].startswith(f"{doc.id}::chunk::")]
                doc_relationships = [r for r in all_relationships if r["chunk_id"].startswith(f"{doc.id}::chunk::")]
                ent_count, rel_count = await self.graph.ingest_document_graph(
                    doc_id=doc.id,
                    chunks=doc_chunks,
                    entities=doc_entities,
                    relationships=doc_relationships,
                )
                entities_created += ent_count
                relationships_created += rel_count
        except Exception as exc:
            errors.append(f"Graph ingestion failed: {exc}")

        return IngestResponse(
            indexed=indexed,
            entities_created=entities_created,
            relationships_created=relationships_created,
            errors=errors,
        )
