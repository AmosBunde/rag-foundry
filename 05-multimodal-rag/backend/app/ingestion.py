import hashlib
import io
from typing import Any

from app.config import settings
from app.embedding import EmbeddingService
from app.llm import LLMClient
from app.models import AudioIngestResponse, ImageIngestResponse, IngestResponse, Modality, TextDocument
from app.retrieval.multimodal import MultimodalRetriever


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


def _stable_id(prefix: str, content: bytes) -> str:
    return f"{prefix}-{hashlib.sha256(content).hexdigest()[:16]}"


class IngestionService:
    """Multimodal ingestion service for text, image, and audio content."""

    def __init__(self) -> None:
        self.retriever = MultimodalRetriever()
        self.embedder = EmbeddingService()
        self.llm = LLMClient()

    async def ingest_text(self, documents: list[TextDocument]) -> IngestResponse:
        items: list[dict[str, Any]] = []
        for doc in documents:
            chunks = _chunk_text(doc.text)
            if not chunks:
                chunks = [doc.text]
            for idx, chunk in enumerate(chunks):
                chunk_id = f"{doc.id}::chunk::{idx}"
                meta = {**doc.metadata, "parent_id": doc.id, "chunk_index": idx}
                items.append({"id": chunk_id, "modality": "text", "content": chunk, "metadata": meta})

        indexed = 0
        errors: list[str] = []
        try:
            indexed += await self.retriever.upsert(items)
        except Exception as exc:  # pragma: no cover
            errors.append(f"Multimodal upsert failed: {exc}")
        return IngestResponse(indexed=indexed, errors=errors)

    async def ingest_image(
        self,
        image_id: str | None,
        filename: str,
        content_type: str,
        image_bytes: bytes,
        metadata: dict[str, Any],
    ) -> ImageIngestResponse:
        """Ingest an image by generating a caption and storing its CLIP-style embedding."""
        try:
            caption = await self.llm.caption_image(f"Describe the image '{filename}' in one sentence.")
        except Exception as exc:  # pragma: no cover
            caption = f"Image upload: {filename}"
            metadata["caption_error"] = str(exc)

        item_id = image_id or _stable_id("img", image_bytes)
        meta = {
            **metadata,
            "filename": filename,
            "content_type": content_type,
            "caption": caption,
        }

        try:
            await self.retriever.upsert(
                [{"id": item_id, "modality": "image", "content": image_bytes, "metadata": meta}]
            )
            return ImageIngestResponse(id=item_id, status="indexed", caption=caption)
        except Exception as exc:  # pragma: no cover
            return ImageIngestResponse(
                id=item_id,
                status="failed",
                caption=caption,
                message=f"Failed to index image: {exc}",
            )

    async def ingest_audio(
        self,
        audio_id: str | None,
        filename: str,
        content_type: str,
        audio_bytes: bytes,
        metadata: dict[str, Any],
    ) -> AudioIngestResponse:
        """Ingest audio by transcribing it to text and storing audio + text embeddings."""
        try:
            transcription = await self.llm.transcribe_audio(audio_bytes)
        except Exception as exc:  # pragma: no cover
            transcription = f"Audio upload: {filename}"
            metadata["transcription_error"] = str(exc)

        item_id = audio_id or _stable_id("audio", audio_bytes)
        meta = {
            **metadata,
            "filename": filename,
            "content_type": content_type,
            "transcription": transcription,
        }

        items: list[dict[str, Any]] = [
            {"id": item_id, "modality": "audio", "content": audio_bytes, "metadata": meta},
        ]
        chunks = _chunk_text(transcription)
        if not chunks:
            chunks = [transcription]
        for idx, chunk in enumerate(chunks):
            items.append(
                {
                    "id": f"{item_id}::chunk::{idx}",
                    "modality": "text",
                    "content": chunk,
                    "metadata": {**meta, "parent_id": item_id, "chunk_index": idx},
                }
            )

        try:
            await self.retriever.upsert(items)
            return AudioIngestResponse(id=item_id, status="indexed", transcription=transcription)
        except Exception as exc:  # pragma: no cover
            return AudioIngestResponse(
                id=item_id,
                status="failed",
                transcription=transcription,
                message=f"Failed to index audio: {exc}",
            )

    async def process_media_async(
        self,
        modality: Modality,
        item_id: str | None,
        filename: str,
        content_type: str,
        file_bytes: bytes,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """Synchronous-style entrypoint for Celery/async workers."""
        if modality == "image":
            result = await self.ingest_image(item_id, filename, content_type, file_bytes, metadata)
            return result.model_dump()
        if modality == "audio":
            result = await self.ingest_audio(item_id, filename, content_type, file_bytes, metadata)
            return result.model_dump()
        raise ValueError(f"Unsupported async modality: {modality}")
