# C2 — Container Diagram: Agentic RAG Hospital

This diagram decomposes the system into its major deployable containers and data stores.

```mermaid
graph TB
    Clinician[Clinician / End User]

    subgraph AgenticRAG [Agentic RAG Hospital — 03-agentic-rag-hospital]
        WebApp[Next.js Frontend<br/>Port 3000]
        APIGateway[FastAPI Backend<br/>Port 8003]
        AuthService[Auth Module<br/>JWT Bearer Tokens]
        Guardrails[Guardrails Module<br/>Regex + Presidio]
        Ingestion[Ingestion Service<br/>Chunking + Dual Indexing]
        Planner[Planner Agent]
        Retriever[Retriever Agent]
        Verifier[Verifier Agent]
        Responder[Responder / Safety Agent]
        AgentGraph[LangGraph Orchestrator]
        LLM[LLM Client]
        Observability[Observability<br/>Metrics / Traces / Logs]
    end

    Clinician -->|HTTPS| WebApp
    Clinician -->|HTTPS / REST| APIGateway
    WebApp -->|Bearer JWT| APIGateway

    APIGateway --> AuthService
    APIGateway --> Guardrails
    APIGateway --> Ingestion
    APIGateway --> AgentGraph
    APIGateway --> Observability

    AgentGraph --> Planner
    AgentGraph --> Retriever
    AgentGraph --> Verifier
    AgentGraph --> Responder

    Retriever -->|Dense search| OllamaEmb[Ollama Embeddings]
    Retriever -->|Vector search| Qdrant[(Qdrant)]
    Retriever -->|BM25| ES[(Elasticsearch)]
    Planner --> LLM
    Verifier --> LLM
    Responder --> LLM
    LLM -->|Generate| OllamaGen[Ollama Generate]

    APIGateway -.->|Rate limit| Redis[(Redis)]
    Observability -->|Metrics| Prometheus[(Prometheus)]
    Observability -->|Traces| OTLP[(OTLP Collector)]
```

## Container Responsibilities

| Container | Responsibility |
|-----------|----------------|
| Next.js Frontend | Browser UI for medical chat, agent reasoning display, ingestion, and patient lookup. |
| FastAPI Backend | HTTP API routing, middleware, exception handling. |
| Auth Module | Issue and validate JWT access tokens. |
| Guardrails Module | Input validation and safety checks. |
| Ingestion Service | Sliding-window chunking and dual indexing into Qdrant and Elasticsearch. |
| Planner Agent | Decides the answering plan and produces a retrieval query. |
| Retriever Agent | Performs hybrid dense + sparse retrieval. |
| Verifier Agent | Checks facts and safety against retrieved sources. |
| Responder Agent | Generates a safe, educational answer or refuses unsafe queries. |
| LangGraph Orchestrator | Manages shared state and transitions between agents. |
| LLM Client | Wraps Ollama `/api/generate` for agent nodes. |
| Observability | Prometheus metrics, OpenTelemetry traces, structlog JSON logs. |
