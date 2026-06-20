# C3 — Component Diagram: Agentic RAG Hospital Backend

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

        subgraph Agents [Agent Graph]
            Planner[planner.py]
            RetrieverAgent[retriever.py]
            Verifier[verifier.py]
            Responder[responder.py]
            Graph[graph.py]
            Service[service.py]
        end

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
    Routers --> Service
    Routers --> LLM
    Routers --> Observability

    Service --> Graph
    Graph --> Planner
    Graph --> RetrieverAgent
    Graph --> Verifier
    Graph --> Responder

    RetrieverAgent --> Dense
    RetrieverAgent --> Sparse
    RetrieverAgent --> Fusion
    Dense -->|embed| Ollama[Ollama]
    Dense -->|vectors| Qdrant[(Qdrant)]
    Sparse -->|BM25| ES[(Elasticsearch)]
    Planner --> LLM
    Verifier --> LLM
    Responder --> LLM

    Ingestion --> Dense
    Ingestion --> Sparse
    Observability -->|traces| OTLP[(OTLP)]
    Observability -->|metrics| Prometheus[(Prometheus)]
```

## Component Responsibilities

| Component | File | Responsibility |
|-----------|------|----------------|
| API Routers | `app/routers/*.py` | Expose `/health`, `/ready`, `/metrics`, `/api/v1/auth`, `/api/v1/ingest`, `/api/v1/query/agent`, `/api/v1/agents/status`, `/api/v1/patients/{id}`. |
| Middleware | `app/main.py` | CORS, trusted host, SlowAPI rate limiting, Prometheus metrics. |
| Auth | `app/auth.py` | JWT token creation/validation and demo user database. |
| Guardrails | `app/guardrails.py` | Length, prompt injection, PII, toxicity, and medical-advice checks. |
| Models | `app/models.py` | Pydantic request/response schemas. |
| Planner Agent | `app/agents/planner.py` | Creates an answering plan and retrieval query. |
| Retriever Agent | `app/agents/retriever.py` | Hybrid dense + sparse retrieval with patient boosting. |
| Verifier Agent | `app/agents/verifier.py` | Safety and coverage verification. |
| Responder Agent | `app/agents/responder.py` | Generates answers or refuses unsafe queries. |
| Graph | `app/agents/graph.py` | Compiles and runs the LangGraph state machine. |
| Service | `app/agents/service.py` | FastAPI-friendly wrapper around the graph. |
| Dense Retriever | `app/retrieval/dense.py` | Ollama embedding + Qdrant cosine search. |
| Sparse Retriever | `app/retrieval/sparse.py` | Elasticsearch BM25 search. |
| RRF Fusion | `app/retrieval/fusion.py` | Reciprocal Rank Fusion of ranked chunk lists. |
| Ingestion Service | `app/ingestion.py` | Chunking and dual-index upsert. |
| LLM Client | `app/llm.py` | Ollama generation and embedding client. |
| Observability | `app/observability.py` | Structlog, OpenTelemetry, Prometheus registry. |
| Config | `app/config.py` | Pydantic-settings based configuration. |
