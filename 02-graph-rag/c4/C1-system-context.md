# C1 — System Context: Graph RAG

This diagram shows the Graph RAG system in its broader environment, including the users and external systems it interacts with.

```mermaid
graph TB
    User[Developer / End User]
    Admin[Platform Administrator]

    subgraph GraphRAG [Graph RAG System]
        GR[02-graph-rag backend]
    end

    User -->|Ingest documents<br/>Query knowledge base| GR
    Admin -->|Monitor metrics & traces<br/>Manage deployments| GR

    GR -->|Embed text| Ollama[Ollama Inference Server]
    GR -->|Vector search| Qdrant[(Qdrant)]
    GR -->|Graph traversal| Neo4j[(Neo4j)]
    GR -->|Rate limit sessions| Redis[(Redis)]
    GR -->|Structured logs| Logs[(Log Aggregation)]
    GR -->|Metrics| Prometheus[(Prometheus / OTLP)]
```

## Description

- **Developer / End User**: consumes the REST API (directly or via the Next.js frontend) to ingest documents and run graph queries.
- **Platform Administrator**: deploys, monitors, and secures the system.
- **Graph RAG backend**: the FastAPI application at the centre of the architecture.
- **Ollama**: local embedding and LLM inference server.
- **Qdrant**: dense vector database.
- **Neo4j**: knowledge graph database.
- **Redis**: session/rate-limit cache.
- **Log Aggregation / Prometheus / OTLP**: observability sinks for JSON logs, metrics, and traces.
