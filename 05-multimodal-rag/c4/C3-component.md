# C3 — Component Diagram: Multi-Modal RAG Backend

This diagram shows the internal components of the FastAPI backend.

```mermaid
graph TB
    Router[API Routers]
    Auth[Auth Component]
    Guardrails[Guardrails Component]
    Health[Health / Metrics]
    IngestText[Text Ingestion]
    IngestImage[Image Ingestion]
    IngestAudio[Audio Ingestion]
    Query[Multimodal Query]
    Embedder[Embedding Service]
    Retriever[Multimodal Retriever]
    LLM[LLM Client]
    CeleryTasks[Celery Tasks]
    Logger[JSON Logger]
    Tracer[OpenTelemetry Tracer]
    Metrics[Prometheus Metrics]

    Router --> Auth
    Router --> Guardrails
    Router --> Health
    Router --> IngestText
    Router --> IngestImage
    Router --> IngestAudio
    Router --> Query

    IngestText --> Embedder
    IngestImage --> LLM
    IngestImage --> Embedder
    IngestAudio --> LLM
    IngestAudio --> Embedder
    Query --> Embedder
    Query --> Retriever

    IngestImage --> CeleryTasks
    IngestAudio --> CeleryTasks

    Router --> Logger
    Router --> Tracer
    Router --> Metrics
```

## Component Responsibilities

- **API Routers**: route HTTP requests to the correct component.
- **Auth Component**: JWT token issuance and validation.
- **Guardrails Component**: input safety checks for text and media.
- **Health / Metrics**: `/health`, `/ready`, `/metrics` endpoints.
- **Text Ingestion**: chunking and embedding of text documents.
- **Image Ingestion**: caption generation and CLIP-style embedding.
- **Audio Ingestion**: transcription and audio/text embedding.
- **Multimodal Query**: embed query and search Qdrant with modality filters.
- **Embedding Service**: modality-aware embedding generation.
- **Multimodal Retriever**: Qdrant search and result mapping.
- **LLM Client**: Ollama-based captioning and transcription.
- **Celery Tasks**: async worker tasks for heavy media processing.
