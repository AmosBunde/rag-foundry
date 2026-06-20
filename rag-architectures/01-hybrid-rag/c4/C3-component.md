# C3 — Component Diagram: Hybrid RAG Backend

This diagram shows the internal components of the FastAPI backend container.

```mermaid
graph TB
    Client[Client]

    subgraph FastAPI [FastAPI Backend]
        Routers[API Routers]
        Middleware[CORS / TrustedHost<br/>Rate Limit / Metrics]
        Auth[auth.py]
        Guardrails[guardrails.py]
        Models[models.py]

        subgraph Retrieval [Retrieval Layer]
            Dense[dense.py<br/>DenseRetriever]
            Sparse[sparse.py<br/>SparseRetriever]
            Fusion[fusion.py<br/>RRF]
        end

        Ingestion[ingestion.py<br/>IngestionService]
        LLM[llm.py<br/>LLMClient]
        Observability[observability.py]
        Config[config.py]
    end

    Client -->|HTTP| Middleware
    Middleware --> Routers
    Routers --> Auth
    Routers --> Guardrails
    Routers --> Models
    Routers --> Ingestion
    Routers --> Dense
    Routers --> Sparse
    Routers --> Fusion
    Routers --> LLM
    Routers --> Observability

    Ingestion --> Dense
    Ingestion --> Sparse
    Dense -->|embed| Ollama[Ollama]
    Dense -->|vectors| Qdrant[(Qdrant)]
    Sparse -->|BM25| ES[(Elasticsearch)]
    LLM -->|generate| Ollama
    Observability -->|traces| OTLP[(OTLP)]
    Observability -->|metrics| Prometheus[(Prometheus)]
```

## Component Responsibilities

| Component | File | Responsibility |
|-----------|------|----------------|
| API Routers | `app/routers/*.py` | Expose `/health`, `/ready`, `/metrics`, `/api/v1/auth`, `/api/v1/ingest`, `/api/v1/query/*`. |
| Middleware | `app/main.py` | CORS, trusted host, SlowAPI rate limiting, Prometheus metrics. |
| Auth | `app/auth.py` | JWT token creation/validation and demo user database. |
| Guardrails | `app/guardrails.py` | Length, prompt injection, PII, and toxicity checks. |
| Models | `app/models.py` | Pydantic request/response schemas. |
| Dense Retriever | `app/retrieval/dense.py` | Ollama embedding + Qdrant cosine search. |
| Sparse Retriever | `app/retrieval/sparse.py` | Elasticsearch BM25 search. |
| RRF Fusion | `app/retrieval/fusion.py` | Reciprocal Rank Fusion of ranked chunk lists. |
| Ingestion Service | `app/ingestion.py` | Chunking and dual-index upsert. |
| LLM Client | `app/llm.py` | Ollama generation client. |
| Observability | `app/observability.py` | Structlog, OpenTelemetry, Prometheus registry. |
| Config | `app/config.py` | Pydantic-settings based configuration. |
