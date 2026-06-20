# C2 — Container Diagram: Graph RAG

This diagram decomposes the Graph RAG system into its major deployable containers and data stores.

```mermaid
graph TB
    User[Developer / End User]

    subgraph GraphRAG [Graph RAG — 02-graph-rag]
        WebApp[Next.js Frontend<br/>Port 3000]
        APIGateway[FastAPI Backend<br/>Port 8002]
        AuthService[Auth Module<br/>JWT Bearer Tokens]
        Guardrails[Guardrails Module<br/>Regex + Presidio]
        Ingestion[Ingestion Service<br/>Chunking + Graph + Vector]
        Query[Query Router<br/>Graph / Vector / Fusion]
        Extractor[Entity Extractor]
        Dense[Dense Retriever]
        Graph[Graph Repository]
        Ranker[Graph Distance Ranker<br/>NetworkX]
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

    Query --> Extractor
    Query --> Dense
    Query --> Graph
    Query --> Ranker
    Dense --> Ranker
    Graph --> Ranker

    Dense -->|HTTP| Ollama[Ollama Embeddings]
    LLM -->|HTTP| OllamaGen[Ollama Generate]
    Dense -->|gRPC/HTTP| Qdrant[(Qdrant)]
    Graph -->|Bolt| Neo4j[(Neo4j)]
    APIGateway -.->|Rate limit| Redis[(Redis)]
    Observability -->|Metrics| Prometheus[(Prometheus)]
    Observability -->|Traces| OTLP[(OTLP Collector)]
```

## Container Responsibilities

| Container | Responsibility |
|-----------|----------------|
| Next.js Frontend | Browser UI for login, chat, ingestion, and graph exploration. |
| FastAPI Backend | HTTP API routing, middleware, exception handling. |
| Auth Module | Issue and validate JWT access tokens. |
| Guardrails Module | Input validation and safety checks. |
| Ingestion Service | Sliding-window chunking, entity extraction, dual indexing into Qdrant and Neo4j. |
| Query Router | Orchestrates graph-aware retrieval endpoints. |
| Entity Extractor | Regex-based extraction of candidate entities from text. |
| Dense Retriever | Embeds text via Ollama and searches Qdrant. |
| Graph Repository | Persists and queries the Neo4j knowledge graph. |
| Graph Distance Ranker | Combines vector scores with graph proximity using NetworkX. |
| LLM Client | Wraps Ollama `/api/generate` for future generation features. |
| Observability | Prometheus metrics, OpenTelemetry traces, structlog JSON logs. |
