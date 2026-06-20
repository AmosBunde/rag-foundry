# C2 — Container Diagram: Multi-Modal RAG

This diagram decomposes the Multi-Modal RAG system into its major deployable containers and data stores.

```mermaid
graph TB
    User[Developer / End User]

    subgraph MultiModalRAG [Multi-Modal RAG — 05-multimodal-rag]
        WebApp[Next.js Frontend<br/>Port 3005]
        APIGateway[FastAPI Backend<br/>Port 8005]
        AuthService[Auth Module<br/>JWT Bearer Tokens]
        Guardrails[Guardrails Module<br/>Regex + Presidio + Media]
        Ingestion[Ingestion Service<br/>Text / Image / Audio]
        Query[Query Router<br/>Multimodal Search]
        Embedder[Embedding Service<br/>Text / Image / Audio]
        Retriever[Multimodal Retriever<br/>Qdrant]
        LLM[LLM Client<br/>Caption + Transcribe]
        CeleryWorker[Celery Worker<br/>Async Media]
        Observability[Observability<br/>Metrics / Traces / Logs]
    end

    User -->|HTTPS| WebApp
    User -->|HTTPS / REST| APIGateway
    WebApp -->|Bearer JWT| APIGateway

    APIGateway --> AuthService
    APIGateway --> Guardrails
    APIGateway --> Ingestion
    APIGateway --> Query
    APIGateway --> Observability

    Ingestion --> Embedder
    Ingestion --> LLM
    Query --> Embedder
    Query --> Retriever
    Retriever --> Qdrant[(Qdrant)]
    Embedder -->|Text embeddings| Ollama[Ollama]
    LLM -->|Generate| Ollama
    APIGateway -.->|Async queue| Redis[(Redis)]
    CeleryWorker -->|Pull tasks| Redis
    CeleryWorker --> Ingestion
    Observability -->|Metrics| Prometheus[(Prometheus)]
    Observability -->|Traces| OTLP[(OTLP Collector)]
```

## Container Responsibilities

| Container | Responsibility |
|-----------|----------------|
| Next.js Frontend | Browser UI for auth, multimodal ingestion, query, and result gallery. |
| FastAPI Backend | HTTP API routing, middleware, exception handling, rate limiting. |
| Auth Module | Issue and validate JWT access tokens. |
| Guardrails Module | Text and media input validation and safety checks. |
| Ingestion Service | Text chunking, image captioning, audio transcription, and upsert. |
| Query Router | `/api/v1/query/multimodal` orchestration. |
| Embedding Service | modality-aware embeddings with Ollama fallback. |
| Multimodal Retriever | Qdrant dense search with modality filters. |
| LLM Client | Ollama wrappers for captioning and transcription. |
| Celery Worker | Async processing of image/audio ingestion tasks. |
| Observability | Prometheus metrics, OpenTelemetry traces, structlog JSON logs. |
