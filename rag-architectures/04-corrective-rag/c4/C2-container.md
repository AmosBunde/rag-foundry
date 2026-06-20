# C2 — Container Diagram: Corrective RAG

This diagram decomposes the Corrective RAG system into its major deployable containers and data stores.

```mermaid
graph TB
    User[Developer / End User]

    subgraph CorrectiveRAG [Corrective RAG — 04-corrective-rag]
        WebApp[Next.js Frontend<br/>Port 3000]
        APIGateway[FastAPI Backend<br/>Port 8004]
        AuthService[Auth Module<br/>JWT Bearer Tokens]
        Guardrails[Guardrails Module<br/>Regex + Presidio]
        Ingestion[Ingestion Service<br/>Chunking + Dual Indexing]
        Query[Query Router<br/>Corrective / Feedback / Hybrid]
        Corrective[Corrective RAG Service]
        Feedback[Feedback Store]
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

    Query --> Corrective
    Query --> Feedback
    Corrective --> Dense
    Corrective --> Sparse
    Corrective --> Fusion
    Corrective --> LLM
    Corrective --> Feedback
    Dense --> Fusion
    Sparse --> Fusion

    Dense -->|HTTP| Ollama[Ollama Embeddings]
    LLM -->|HTTP| OllamaGen[Ollama Generate / Evaluate / Rewrite]
    Dense -->|gRPC/HTTP| Qdrant[(Qdrant)]
    Sparse -->|HTTP| ES[(Elasticsearch)]
    APIGateway -.->|Rate limit| Redis[(Redis)]
    Observability -->|Metrics| Prometheus[(Prometheus)]
    Observability -->|Traces| OTLP[(OTLP Collector)]
```

## Container Responsibilities

| Container | Responsibility |
|-----------|----------------|
| Next.js Frontend | Browser UI for ingestion, corrective queries, iteration inspection, and feedback. |
| FastAPI Backend | HTTP API routing, middleware, exception handling. |
| Auth Module | Issue and validate JWT access tokens. |
| Guardrails Module | Input validation and safety checks. |
| Ingestion Service | Sliding-window chunking and dual indexing into Qdrant and Elasticsearch. |
| Query Router | Orchestrates corrective, feedback, hybrid, dense, and sparse endpoints. |
| Corrective RAG Service | Runs the confidence-driven rewrite/re-retrieve loop and generates answers. |
| Feedback Store | Records user feedback and computes per-result helpfulness scores. |
| Dense Retriever | Embeds text via Ollama and searches Qdrant. |
| Sparse Retriever | Searches Elasticsearch with BM25. |
| RRF Fusion Engine | Combines ranked lists using Reciprocal Rank Fusion. |
| LLM Client | Wraps Ollama for generation, relevance evaluation, and query rewriting. |
| Observability | Prometheus metrics, OpenTelemetry traces, structlog JSON logs. |
