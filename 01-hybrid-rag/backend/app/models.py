from typing import Any

from pydantic import BaseModel, Field, field_validator


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    service: str = "hybrid-rag"


class ReadyResponse(BaseModel):
    ready: bool
    checks: dict[str, bool]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Document(BaseModel):
    id: str
    text: str = Field(..., min_length=1, max_length=100_000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class IngestRequest(BaseModel):
    documents: list[Document] = Field(..., min_length=1, max_length=100)

    @field_validator("documents")
    @classmethod
    def _validate_unique_ids(cls, documents: list[Document]) -> list[Document]:
        ids = [doc.id for doc in documents]
        if len(ids) != len(set(ids)):
            raise ValueError("Document IDs must be unique")
        return documents


class IngestResponse(BaseModel):
    indexed: int
    errors: list[str] = Field(default_factory=list)


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2_000)
    top_k: int = Field(default=5, ge=1, le=50)
    use_dense: bool = True
    use_sparse: bool = True


class RetrievedChunk(BaseModel):
    id: str
    text: str
    score: float
    metadata: dict[str, Any]
    source: str  # "dense" | "sparse" | "fusion"


class QueryResponse(BaseModel):
    query: str
    results: list[RetrievedChunk]
    latency_ms: float


class DenseRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2_000)
    top_k: int = Field(default=5, ge=1, le=50)


class SparseRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2_000)
    top_k: int = Field(default=5, ge=1, le=50)
