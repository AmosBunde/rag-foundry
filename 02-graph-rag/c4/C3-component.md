# C3 — Component Diagram: Graph RAG Backend

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
            Ranker[ranker.py<br/>Graph Distance]
        end

        subgraph GraphLayer [Graph Layer]
            Graph[graph.py<br/>GraphRepository]
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
    Routers --> Graph
    Routers --> Ranker
    Routers --> LLM
    Routers --> Observability

    Ingestion --> Dense
    Ingestion --> Graph
    Dense -->|embed| Ollama[Ollama]
    Dense -->|vectors| Qdrant[(Qdrant)]
    Graph -->|Bolt| Neo4j[(Neo4j)]
    Ranker -->|shortest paths| NetworkX[NetworkX]
    LLM -->|generate| Ollama
    Observability -->|traces| OTLP[(OTLP)]
    Observability -->|metrics| Prometheus[(Prometheus)]
```

## Component Responsibilities

| Component | File | Responsibility |
|-----------|------|----------------|
| API Routers | `app/routers/*.py` | Expose `/health`, `/ready`, `/metrics`, `/api/v1/auth`, `/api/v1/ingest`, `/api/v1/query/graph`, `/api/v1/graph/*`. |
| Middleware | `app/main.py` | CORS, trusted host, SlowAPI rate limiting, Prometheus metrics. |
| Auth | `app/auth.py` | JWT token creation/validation and demo user database. |
| Guardrails | `app/guardrails.py` | Length, prompt injection, PII, and toxicity checks. |
| Models | `app/models.py` | Pydantic request/response schemas. |
| Dense Retriever | `app/retrieval/dense.py` | Ollama embedding + Qdrant cosine search. |
| Graph Distance Ranker | `app/retrieval/ranker.py` | NetworkX graph distance + score fusion. |
| Graph Repository | `app/graph.py` | Neo4j ingestion, traversal, entity expansion. |
| Ingestion Service | `app/ingestion.py` | Chunking, entity extraction, dual-index upsert. |
| LLM Client | `app/llm.py` | Ollama generation client. |
| Observability | `app/observability.py` | Structlog, OpenTelemetry, Prometheus registry. |
| Config | `app/config.py` | Pydantic-settings based configuration. |
