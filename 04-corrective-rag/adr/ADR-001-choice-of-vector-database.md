# ADR 001: Choice of Vector Database and Sparse Retrieval Store

## Status

Accepted

## Context

The Corrective RAG architecture requires two complementary retrieval mechanisms:

1. A **dense vector store** for semantic similarity search over embedding vectors.
2. A **sparse lexical store** for keyword/BM25-style search.

The chosen stores must run locally for development, deploy to common cloud platforms, and integrate cleanly with Python async code.

## Decision

Use **Qdrant** for dense retrieval and **Elasticsearch** for sparse retrieval.

- **Qdrant** stores 768-dimensional dense vectors produced by the `nomic-embed-text` embedding model. It is queried with cosine similarity.
- **Elasticsearch** indexes the same chunked documents as Qdrant and is queried with a standard `match` query for BM25 scoring.
- Both stores are created automatically on first use if the collection/index does not exist.

## Consequences

- Positive: Qdrant and Elasticsearch both have official, well-maintained Python clients (`qdrant-client`, `elasticsearch`).
- Positive: Both can run in Docker locally and have managed cloud offerings (Qdrant Cloud, Elastic Cloud, AWS OpenSearch, Azure Cognitive Search, GCP Elasticsearch).
- Positive: Decoupling dense and sparse stores allows independent scaling, tuning, and operational ownership.
- Negative: Two data stores increase operational complexity (backup, monitoring, schema drift).
- Negative: Elasticsearch 8.x requires explicit security configuration in production.

## Alternatives Considered

- **Single store with hybrid search** (e.g., OpenSearch or pgvector with sparse-dense vectors): simplifies operations but couples tuning and may not expose first-class BM25 controls.
- **Pinecone for dense + Elasticsearch for sparse**: Pinecone is easy to operate but adds a third-party dependency and less flexibility for local/offline development.
- **Weaviate for both**: supports vector and BM25 in one system, but the team already had operational experience with Elasticsearch and Qdrant.

## References

- [Qdrant documentation](https://qdrant.tech/documentation/)
- [Elasticsearch BM25 scoring](https://www.elastic.co/guide/en/elasticsearch/reference/current/index-modules-similarity.html)
- [Reciprocal Rank Fusion paper, Cormack et al.](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)
