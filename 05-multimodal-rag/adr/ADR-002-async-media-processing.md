# ADR 002: Async Media Processing

## Status

Accepted

## Context

Image captioning and audio transcription are CPU/GPU-intensive and can exceed HTTP request timeouts. The system needs a way to offload heavy media ingestion without blocking API clients.

## Decision

Use **Celery** with **Redis** as the broker and result backend for asynchronous media processing.

- Synchronous endpoints (`/api/v1/ingest/image`, `/api/v1/ingest/audio`) handle small files and return immediately.
- Async endpoints (`/api/v1/ingest/image/async`, `/api/v1/ingest/audio/async`) queue Celery tasks and return a `task_id`.
- Celery workers run the same ingestion service code in a separate container.
- In development and tests, `CELERY_TASK_ALWAYS_EAGER=true` runs tasks inline.

## Consequences

- Positive: API remains responsive for large uploads.
- Positive: Workers can be scaled independently.
- Negative: Adds operational complexity (worker monitoring, result expiry, retry logic).
