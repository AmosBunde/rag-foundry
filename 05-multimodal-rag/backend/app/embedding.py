import hashlib
from typing import Any

import httpx
import numpy as np

from app.config import settings


def _stable_seed(value: str) -> int:
    return int(hashlib.sha256(value.encode("utf-8")).hexdigest()[:16], 16)


def _mock_vector(seed_text: str, size: int = settings.vector_size) -> list[float]:
    """Generate a deterministic unit-normalized mock embedding."""
    rng = np.random.default_rng(_stable_seed(seed_text))
    vector = rng.standard_normal(size)
    vector = vector / np.linalg.norm(vector)
    return vector.astype(float).tolist()


class EmbeddingService:
    """Generates multimodal embeddings. Falls back to deterministic mocks when Ollama is unavailable."""

    def __init__(self) -> None:
        self.ollama_url = settings.ollama_url
        self.model = settings.embedding_model
        self.vector_size = settings.vector_size
        self.mock_mode = settings.mock_embeddings

    async def embed_text(self, texts: list[str]) -> list[list[float]]:
        """Embed text via Ollama or deterministic mock vectors."""
        if not texts:
            return []
        if self.mock_mode:
            return [_mock_vector(text, self.vector_size) for text in texts]

        embeddings: list[list[float]] = []
        async with httpx.AsyncClient() as client:
            for text in texts:
                try:
                    response = await client.post(
                        f"{self.ollama_url}/api/embeddings",
                        json={"model": self.model, "prompt": text},
                        timeout=60.0,
                    )
                    response.raise_for_status()
                    data = response.json()
                    vector = np.array(data["embedding"])
                    if vector.shape[0] != self.vector_size:
                        vector = self._project(vector, self.vector_size)
                    embeddings.append(vector.tolist())
                except Exception:
                    embeddings.append(_mock_vector(text, self.vector_size))
        return embeddings

    async def embed_image(self, image_bytes_list: list[bytes]) -> list[list[float]]:
        """Mock CLIP-style image embeddings. Production should use a vision encoder."""
        return [_mock_vector(f"image:{hashlib.sha256(img).hexdigest()}", self.vector_size) for img in image_bytes_list]

    async def embed_audio(self, audio_bytes_list: list[bytes]) -> list[list[float]]:
        """Mock audio embeddings. Production should use an audio encoder."""
        return [_mock_vector(f"audio:{hashlib.sha256(audio).hexdigest()}", self.vector_size) for audio in audio_bytes_list]

    def _project(self, vector: np.ndarray, target_size: int) -> np.ndarray:
        """Project a vector to target_size by padding or truncating, then normalize."""
        if vector.shape[0] >= target_size:
            projected = vector[:target_size]
        else:
            projected = np.pad(vector, (0, target_size - vector.shape[0]))
        norm = np.linalg.norm(projected)
        if norm > 0:
            projected = projected / norm
        return projected

    async def embed_modality(self, modality: str, payloads: list[Any]) -> list[list[float]]:
        if modality == "text":
            return await self.embed_text([str(p) for p in payloads])
        if modality == "image":
            return await self.embed_image([p if isinstance(p, bytes) else str(p).encode() for p in payloads])
        if modality == "audio":
            return await self.embed_audio([p if isinstance(p, bytes) else str(p).encode() for p in payloads])
        raise ValueError(f"Unsupported modality: {modality}")
