# ADR 001: Choice of Vector Database and Knowledge Graph Store

## Status

Accepted

## Context

The Graph RAG architecture requires:

1. A **dense vector store** for semantic similarity search over embedding vectors.
2. A **knowledge graph store** for entity and relationship storage, traversal, and graph-distance ranking.

Both stores must run locally for development, deploy to common cloud platforms, and integrate cleanly with Python async code.

## Decision

Use **Qdrant** for dense retrieval and **Neo4j** for the knowledge graph.

- **Qdrant** stores 768-dimensional dense vectors produced by the `nomic-embed-text` embedding model. It is queried with cosine similarity.
- **Neo4j** stores `(:Entity)`, `(:Chunk)`, and `(:Document)` nodes plus `MENTIONS` and `CO_OCCURS_WITH` relationships.
- During ingestion, text is chunked, embedded into Qdrant, and lightweight regex entity extraction populates Neo4j.
- During query, entities are extracted from the query, Neo4j traverses the graph to find nearby chunks, and results are re-ranked by graph distance using NetworkX.

## Consequences

- Positive: Qdrant and Neo4j both have official, well-maintained Python clients (`qdrant-client`, `neo4j`).
- Positive: Both run in Docker locally and have managed cloud offerings (Qdrant Cloud, Neo4j Aura, AWS/Azure/GCP marketplaces).
- Positive: Graph traversal surfaces relationship-based evidence that pure vector search can miss.
- Negative: Two data stores increase operational complexity (backup, monitoring, schema drift).
- Negative: Entity extraction is currently regex-based; accuracy is lower than spaCy or LLM extractors.

## Alternatives Considered

- **Single store with vector + graph** (e.g., Neo4j GDS or Weaviate): reduces operations but couples tuning and limits deployment options.
- **Pinecone for dense + Neo4j for graph**: Pinecone is easy but adds a third-party dependency and less flexibility for offline development.
- **ArangoDB for both**: supports documents, graphs, and vectors, but less community familiarity in the team.

## References

- [Qdrant documentation](https://qdrant.tech/documentation/)
- [Neo4j Python Driver](https://neo4j.com/docs/python-manual/current/)
- [NetworkX shortest paths](https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html)
