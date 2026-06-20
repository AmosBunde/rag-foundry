# ADR 002: Choice of LLM and Embedding Framework

## Status

Accepted

## Context

The multi-agent system needs an LLM for planning, verification, and response generation, plus embeddings for dense retrieval. The framework should work offline and expose a simple HTTP API.

## Decision

Use **Ollama** as the local inference server for both embeddings and generation.

- **Embedding model**: `nomic-embed-text` (768-dimensional output).
- **LLM**: `llama3:8b` for planning, verification, and response generation.
- The backend calls Ollama's `/api/embeddings` and `/api/generate` endpoints via `httpx.AsyncClient`.

## Consequences

- Positive: No cloud API keys required for local development.
- Positive: Switching to a cloud provider later only requires changing the URL and payload format.
- Negative: Local throughput and latency are limited by host CPU/GPU.
- Negative: Medical accuracy depends on the chosen open model; production may require a medically tuned model.

## Alternatives Considered

- **OpenAI / Azure OpenAI**: higher quality for many tasks but requires keys and cost governance.
- **Hugging Face Transformers in-process**: removes a network hop but increases image size and complexity.

## References

- [Ollama REST API](https://github.com/ollama/ollama/blob/main/docs/api.md)
