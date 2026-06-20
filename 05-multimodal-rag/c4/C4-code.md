# C4 — Code Diagram: Multi-Modal RAG Backend

This diagram illustrates the key code-level relationships in the FastAPI backend.

```mermaid
classDiagram
    class main {
        +FastAPI app
        +lifespan()
        +middleware()
    }
    class routers_health {
        +health()
        +ready()
        +metrics()
    }
    class routers_auth {
        +login()
    }
    class routers_ingest {
        +ingest_text()
        +ingest_image()
        +ingest_audio()
        +ingest_image_async()
        +ingest_audio_async()
    }
    class routers_query {
        +multimodal_query()
    }
    class ingestion {
        +IngestionService
        +ingest_text()
        +ingest_image()
        +ingest_audio()
        +process_media_async()
    }
    class retrieval_multimodal {
        +MultimodalRetriever
        +upsert()
        +search()
    }
    class embedding {
        +EmbeddingService
        +embed_text()
        +embed_image()
        +embed_audio()
    }
    class llm {
        +LLMClient
        +generate()
        +caption_image()
        +transcribe_audio()
    }
    class tasks {
        +celery_app
        +process_media()
    }
    class guardrails {
        +validate_query()
        +validate_media_metadata()
    }
    class observability {
        +configure_logging()
        +configure_tracing()
        +metrics_middleware()
    }

    main --> routers_health
    main --> routers_auth
    main --> routers_ingest
    main --> routers_query
    routers_ingest --> ingestion
    routers_query --> retrieval_multimodal
    ingestion --> retrieval_multimodal
    ingestion --> embedding
    ingestion --> llm
    retrieval_multimodal --> embedding
    tasks --> ingestion
    routers_ingest --> tasks
    main --> observability
    routers_ingest --> guardrails
    routers_query --> guardrails
```

## Key Modules

| File | Responsibility |
|------|----------------|
| `app/main.py` | FastAPI application assembly and middleware. |
| `app/routers/health.py` | Health, readiness, and Prometheus metrics endpoints. |
| `app/routers/auth.py` | OAuth2 password login and JWT issuance. |
| `app/routers/ingest.py` | Text, image, and audio ingestion endpoints. |
| `app/routers/query.py` | Multimodal query endpoint. |
| `app/ingestion.py` | Ingestion service for all modalities. |
| `app/retrieval/multimodal.py` | Qdrant-based multimodal retriever. |
| `app/embedding.py` | Embedding service with mock and Ollama paths. |
| `app/llm.py` | LLM client for generation, captioning, transcription. |
| `app/tasks.py` | Celery app and async media processing task. |
| `app/guardrails.py` | Text and media safety checks. |
| `app/observability.py` | Logging, tracing, and metrics. |
