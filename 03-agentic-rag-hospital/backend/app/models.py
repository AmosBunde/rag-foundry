from typing import Any

from pydantic import BaseModel, Field, field_validator


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    service: str = "agentic-rag-hospital"


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


class AgentQueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2_000)
    patient_id: str | None = Field(default=None, max_length=256)
    top_k: int = Field(default=5, ge=1, le=50)


class ReasoningStep(BaseModel):
    agent: str
    step: str
    detail: str | dict[str, Any] | None = None


class RetrievedChunk(BaseModel):
    id: str
    text: str
    score: float
    metadata: dict[str, Any]
    source: str


class AgentQueryResponse(BaseModel):
    query: str
    answer: str
    plan: list[str]
    reasoning: list[ReasoningStep]
    sources: list[RetrievedChunk]
    safety_checks_passed: bool
    disclaimer: str
    latency_ms: float


class AgentStatusResponse(BaseModel):
    agents: dict[str, str]
    ready: bool


class PatientSummary(BaseModel):
    patient_id: str
    name: str
    birth_date: str
    gender: str
    conditions: list[str]
    medications: list[str]
    allergies: list[str]
