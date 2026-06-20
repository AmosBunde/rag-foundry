# ADR 001: Multi-Modal Vector Store

## Status

Accepted

## Context

The Multi-Modal RAG architecture must store and retrieve text, image, and audio content in a single, unified retrieval surface. Each modality needs an embedding representation that can be compared with cosine similarity.

## Decision

Use **Qdrant** as the single vector store for all modalities.

- All embeddings are projected into a shared 512-dimensional space.
- Text embeddings are generated via Ollama (`nomic-embed-text`) with fallback to deterministic mock vectors.
- Image and audio embeddings use deterministic mock CLIP-style / audio embeddings (production should use a vision encoder and audio encoder).
- Each point payload includes `modality` (`text`, `image`, or `audio`), `content`, and `metadata`.
- Queries can be filtered by modality.

## Consequences

- Positive: One store simplifies operations and cross-modal retrieval.
- Positive: Qdrant supports payload filters, enabling per-modality search.
- Negative: Shared vector spaces require consistent dimensionality; production needs real multimodal encoders.
- Negative: Mock embeddings are not semantically aligned across modalities.
