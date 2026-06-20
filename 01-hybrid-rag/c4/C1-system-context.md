# C1 — System Context: Hybrid RAG

This diagram shows the Hybrid RAG system in its broader environment, including the users and external systems it interacts with.

```mermaid
graph TB
    User[Developer / End User]
    Admin[Platform Administrator]

    subgraph HybridRAG [Hybrid RAG System]
        HR[01-hybrid-rag backend]
    end

    User -->|Ingest documents<br/>Query knowledge base| HR
    Admin -->|Monitor metrics & traces<br/>Manage deployments| HR

    HR -->|Embed text| Ollama[Ollama Inference Server]
    HR -->|Vector search| Qdrant[(Qdrant)]
    HR -->|BM25 search| ES[(Elasticsearch)]
    HR -->|Rate limit sessions| Redis[(Redis)]
    HR -->|Structured logs| Logs[(Log Aggregation)]
    HR -->|Metrics| Prometheus[(Prometheus / OTLP)]
```

## Description

- **Developer / End User**: consumes the REST API (directly or via the Next.js frontend) to ingest documents and run hybrid queries.
- **Platform Administrator**: deploys, monitors, and secures the system.
- **Hybrid RAG backend**: the FastAPI application at the centre of the architecture.
- **Ollama**: local embedding and LLM inference server.
- **Qdrant**: dense vector database.
- **Elasticsearch**: sparse lexical database.
- **Redis**: session/rate-limit cache.
- **Log Aggregation / Prometheus / OTLP**: observability sinks for JSON logs, metrics, and traces.
