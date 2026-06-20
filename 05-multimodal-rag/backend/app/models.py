from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    service: str = "multimodal-rag"


class ReadyResponse(BaseModel):
    ready: bool
    checks: dict[str, bool]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


Modality = Literal["text", "image", "audio"]


class MultimodalResult(BaseModel):
    id: str
    modality: Modality
    content: str
    score: float
    metadata: dict[str, Any]


class TextDocument(BaseModel):
    id: str
    text: str = Field(..., min_length=1, max_length=100_000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TextIngestRequest(BaseModel):
    documents: list[TextDocument] = Field(..., min_length=1, max_length=100)

    @field_validator("documents")
    @classmethod
    def _validate_unique_ids(cls, documents: list[TextDocument]) -> list[TextDocument]:
        ids = [doc.id for doc in documents]
        if len(ids) != len(set(ids)):
            raise ValueError("Document IDs must be unique")
        return documents


class ImageIngestResponse(BaseModel):
    id: str
    status: str
    caption: str | None = None
    message: str | None = None


class AudioIngestResponse(BaseModel):
    id: str
    status: str
    transcription: str | None = None
    message: str | None = None


class IngestResponse(BaseModel):
    indexed: int
    errors: list[str] = Field(default_factory=list)


class MultimodalQueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2_000)
    top_k: int = Field(default=5, ge=1, le=50)
    modalities: list[Modality] = Field(default_factory=lambda: ["text", "image", "audio"])

    @field_validator("modalities")
    @classmethod
    def _validate_modalities(cls, modalities: list[Modality]) -> list[Modality]:
        if not modalities:
            raise ValueError("At least one modality must be selected")
        if len(set(modalities)) != len(modalities):
            raise ValueError("Modalities must be unique")
        return modalities


class MultimodalQueryResponse(BaseModel):
    query: str
    results: list[MultimodalResult]
    latency_ms: float
    modalities: list[Modality]
