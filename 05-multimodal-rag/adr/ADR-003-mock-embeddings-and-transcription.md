# ADR 003: Mock Embeddings and Transcription

## Status

Accepted

## Context

Production-grade image encoders (CLIP), audio encoders, and speech-to-text (Whisper) require heavy dependencies and model weights. For a local development template, we need lightweight, deterministic stand-ins.

## Decision

Provide mock embeddings and transcription with optional Ollama integration.

- `EmbeddingService` generates deterministic unit-normalized vectors seeded by content hash.
- For text, it attempts Ollama first and falls back to mock vectors.
- `LLMClient` provides `caption_image` and `transcribe_audio` methods that call Ollama's generate endpoint with prompt engineering.
- A `MOCK_EMBEDDINGS=true` flag forces mock mode even when Ollama is available.

## Consequences

- Positive: The template works without GPU or large model downloads.
- Positive: Production paths are clearly marked in code.
- Negative: Retrieval quality is not representative until real encoders are wired in.
