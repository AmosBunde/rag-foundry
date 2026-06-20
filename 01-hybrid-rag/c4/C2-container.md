# C2 — Container Diagram: Hybrid RAG

This diagram decomposes the Hybrid RAG system into its major deployable containers and data stores.

```mermaid
graph TB
    User[Developer / End User]

    subgraph HybridRAG [Hybrid RAG — 01-hybrid-rag]
        WebApp[Next.js Frontend<br/>Port 3000]
        APIGateway[FastAPI Backend<br/>Port 8001]
        AuthService[Auth Module<br/>JWT Bearer Tokens]
        Guardrails[Guardrails Module<br/>Regex + Presidio]
        Ingestion[Ingestion Service<br/>Chunking + Dual Indexing]
        Query[Query Router<br/>Hybrid / Dense / Sparse]
        Dense[Dense Retriever]
        Sparse[Sparse Retriever]
        Fusion[RRF Fusion Engine]
        LLM[LLM Client]
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

    Query --> Dense
    Query --> Sparse
    Dense --> Fusion
    Sparse --> Fusion
    Query --> Fusion
    APIGateway --> LLM

    Dense -->|HTTP| Ollama[Ollama Embeddings]
    LLM -->|HTTP| OllamaGen[Ollama Generate]
    Dense -->|gRPC/HTTP| Qdrant[(Qdrant)]
    Sparse -->|HTTP| ES[(Elasticsearch)]
    APIGateway -.->|Rate limit| Redis[(Redis)]
    Observability -->|Metrics| Prometheus[(Prometheus)]
    Observability -->|Traces| OTLP[(OTLP Collector)]
```

## Container Responsibilities

| Container | Responsibility |
|-----------|----------------|
| Next.js Frontend | Browser UI for ingestion, queries, and results (scaffold). |
| FastAPI Backend | HTTP API routing, middleware, exception handling. |
| Auth Module | Issue and validate JWT access tokens. |
| Guardrails Module | Input validation and safety checks. |
| Ingestion Service | Sliding-window chunking and dual indexing into Qdrant and Elasticsearch. |
| Query Router | Orchestrates dense, sparse, and fused search endpoints. |
| Dense Retriever | Embeds text via Ollama and searches Qdrant. |
| Sparse Retriever | Searches Elasticsearch with BM25. |
| RRF Fusion Engine | Combines ranked lists using Reciprocal Rank Fusion. |
| LLM Client | Wraps Ollama `/api/generate` for future generation features. |
| Observability | Prometheus metrics, OpenTelemetry traces, structlog JSON logs. |
