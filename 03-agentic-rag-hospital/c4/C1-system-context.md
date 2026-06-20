# C1 — System Context: Agentic RAG Hospital

This diagram shows the Agentic RAG Hospital system in its broader environment, including users and external systems.

```mermaid
graph TB
    Clinician[Clinician / End User]
    Admin[Platform Administrator]

    subgraph AgenticRAG [Agentic RAG Hospital System]
        ARH[03-agentic-rag-hospital backend]
    end

    Clinician -->|Ask medical question<br/>View patient summary| ARH
    Admin -->|Monitor metrics & traces<br/>Manage deployments| ARH

    ARH -->|Embed text / generate text| Ollama[Ollama Inference Server]
    ARH -->|Vector search| Qdrant[(Qdrant)]
    ARH -->|BM25 search| ES[(Elasticsearch)]
    ARH -->|Rate limit sessions| Redis[(Redis)]
    ARH -->|Structured logs| Logs[(Log Aggregation)]
    ARH -->|Metrics / traces| Prometheus[(Prometheus / OTLP)]
```

## Description

- **Clinician / End User**: consumes the REST API (directly or via the Next.js frontend) to ask medical questions and view patient summaries.
- **Platform Administrator**: deploys, monitors, and secures the system.
- **Agentic RAG Hospital backend**: the FastAPI application orchestrating planner, retriever, verifier, and responder agents.
- **Ollama**: local embedding and LLM inference server.
- **Qdrant**: dense vector database.
- **Elasticsearch**: sparse lexical database.
- **Redis**: session/rate-limit cache.
- **Log Aggregation / Prometheus / OTLP**: observability sinks for JSON logs, metrics, and traces.
