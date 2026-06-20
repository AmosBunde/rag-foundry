# ADR 002: Choice of LLM and Embedding Framework

## Status

Accepted

## Context

The architecture needs:

1. An **embedding model** to convert queries and documents into dense vectors for Qdrant.
2. An **LLM** to evaluate retrieval relevance, rewrite low-confidence queries, and generate answers.

The framework should work offline, require no cloud API keys for local development, and expose a simple HTTP API that the FastAPI backend can call asynchronously.

## Decision

Use **Ollama** as the local inference server for both embeddings and generation.

- **Embedding model**: `nomic-embed-text` (768-dimensional output).
- **LLM**: `llama3:8b` for local generation tasks.
- The backend calls Ollama's `/api/embeddings`, `/api/generate`, and relevance-evaluation prompts via `httpx.AsyncClient`.
- Ollama is included as a service in the root `docker-compose.yml` and can also run natively on the developer's machine.

## Consequences

- Positive: No cloud API keys or network egress required for local development.
- Positive: Ollama supports a wide range of open models and keeps model management simple (`ollama pull <model>`).
- Positive: Switching to a cloud provider later only requires changing the URL and payload format in `app/llm.py` and `app/retrieval/dense.py`.
- Negative: Local GPU/CPU performance limits throughput and latency compared to hosted APIs.
- Negative: Embedding requests are made sequentially in `DenseRetriever.embed()`; batching should be added for high-throughput workloads.

## Alternatives Considered

- **OpenAI / Azure OpenAI**: lower latency and higher quality for many tasks, but requires API keys, network egress, and cost governance.
- **Hugging Face Transformers (in-process)**: removes a network hop but increases image size, memory footprint, and complexity for model versioning.
- **Sentence-Transformers + local LLM server**: works well for embeddings but lacks the unified model management of Ollama.

## References

- [Ollama REST API](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [nomic-embed-text model card](https://huggingface.co/nomic-ai/nomic-embed-text-v1)
- [Llama 3 model card](https://ai.meta.com/blog/meta-llama-3/)
