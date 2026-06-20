# C1 — System Context: Corrective RAG

This diagram shows the Corrective RAG system in its broader environment, including the users and external systems it interacts with.

```mermaid
graph TB
    User[Developer / End User]
    Admin[Platform Administrator]

    subgraph CorrectiveRAG [Corrective RAG System]
        CR[04-corrective-rag backend]
    end

    User -->|Ingest documents<br/>Query knowledge base<br/>Submit feedback| CR
    Admin -->|Monitor metrics & traces<br/>Manage deployments| CR

    CR -->|Embed text| Ollama[Ollama Inference Server]
    CR -->|Evaluate relevance / rewrite / answer| Ollama
    CR -->|Vector search| Qdrant[(Qdrant)]
    CR -->|BM25 search| ES[(Elasticsearch)]
    CR -->|Rate limit sessions| Redis[(Redis)]
    CR -->|Structured logs| Logs[(Log Aggregation)]
    CR -->|Metrics| Prometheus[(Prometheus / OTLP)]
```

## Description

- **Developer / End User**: consumes the REST API (directly or via the Next.js frontend) to ingest documents, run corrective queries, and submit feedback.
- **Platform Administrator**: deploys, monitors, and secures the system.
- **Corrective RAG backend**: the FastAPI application at the centre of the architecture.
- **Ollama**: local embedding, relevance evaluation, query rewriting, and answer generation.
- **Qdrant**: dense vector database.
- **Elasticsearch**: sparse lexical database.
- **Redis**: session/rate-limit cache.
- **Log Aggregation / Prometheus / OTLP**: observability sinks for JSON logs, metrics, and traces.
