# C4 — Code Diagram: Graph RAG Backend

This diagram zooms into the key classes and functions that implement graph retrieval and ingestion.

```mermaid
classDiagram
    class FastAPI {
        +lifespan
        +include_router()
    }

    class QueryRouter {
        +graph_query(request: GraphQueryRequest)
    }

    class IngestRouter {
        +ingest_documents(request: IngestRequest)
    }

    class GraphRouter {
        +list_entities(name, limit)
        +expand_entity(entity_id, depth)
    }

    class DenseRetriever {
        -client: QdrantClient
        -collection: str
        -ollama_url: str
        -model: str
        +embed(texts: list[str]) list[list[float]]
        +upsert(documents) int
        +search(query: str, top_k: int) list[RetrievedChunk]
    }

    class GraphRepository {
        -driver: AsyncDriver
        +ingest_document_graph(doc_id, chunks, entities, relationships)
        +get_entities(name_query, limit) list[Entity]
        +expand_entity(entity_id, depth) ExpandResponse
        +get_chunk_ids_near_entities(entity_ids, depth) dict
    }

    class IngestionService {
        -dense: DenseRetriever
        -graph: GraphRepository
        +ingest(documents) IngestResponse
        -_chunk_text(text, chunk_size, overlap) list[str]
    }

    class Ranker {
        +build_nx_graph(edges) Graph
        +graph_distance_matrix(graph, sources, targets) dict
        +rank_by_graph_distance(vector_results, graph_distances, top_k) list[RetrievedChunk]
    }

    class Guardrails {
        +validate_query(text, max_length, use_presidio) GuardrailResult
        +guard_query(text, max_length) void
    }

    class Auth {
        +authenticate_user(username, password) UserInDB
        +create_access_token(data, expires_delta) str
        +get_current_user(token) User
    }

    class RetrievedChunk {
        +id: str
        +text: str
        +score: float
        +metadata: dict
        +source: str
    }

    FastAPI --> QueryRouter
    FastAPI --> IngestRouter
    FastAPI --> GraphRouter
    QueryRouter --> DenseRetriever
    QueryRouter --> GraphRepository
    QueryRouter --> Ranker
    QueryRouter --> Guardrails
    IngestRouter --> IngestionService
    GraphRouter --> GraphRepository
    IngestionService --> DenseRetriever
    IngestionService --> GraphRepository
    DenseRetriever ..> RetrievedChunk
    Ranker ..> RetrievedChunk
    QueryRouter --> Auth
    IngestRouter --> Auth
    GraphRouter --> Auth
```

## Key Code Paths

### Graph query

```python
# app/routers/query.py
@router.post("/graph", response_model=QueryResponse)
async def graph_query(
    request: GraphQueryRequest,
    user: User = Depends(get_current_user),
    dense: DenseRetriever = Depends(_get_dense),
    graph: GraphRepository = Depends(_get_graph),
) -> QueryResponse:
    guard_query(request.query)
    query_entities = extract_entities(request.query, chunk_id="query")
    vector_results = await dense.search(request.query, top_k=request.top_k * 2)
    graph_distances = await graph.get_chunk_ids_near_entities(
        [e["id"] for e in query_entities], depth=request.graph_depth
    )
    results = rank_by_graph_distance(vector_results, graph_distances, top_k=request.top_k)
    return QueryResponse(query=request.query, results=results, latency_ms=...)
```

### Graph ingestion

```python
# app/ingestion.py
async def ingest(self, documents: list[Document]) -> IngestResponse:
    for doc in documents:
        chunks = _chunk_text(doc.text)
        for idx, chunk_text in enumerate(chunks):
            chunk_id = f"{doc.id}::chunk::{idx}"
            entities = extract_entities(chunk_text, chunk_id)
            relationships = build_relationships(entities, chunk_id)
            await self.dense.upsert([...])
            await self.graph.ingest_document_graph(
                doc.id, chunks, entities, relationships
            )
    return IngestResponse(indexed=..., entities_created=..., relationships_created=...)
```

### Graph distance ranking

```python
# app/retrieval/ranker.py
def rank_by_graph_distance(vector_results, graph_distances, top_k=5, distance_weight=0.5):
    scored = []
    for chunk in vector_results:
        distance = graph_distances.get(chunk.id)
        graph_score = 1.0 / (1.0 + distance) if distance is not None else 0
        combined = (1 - distance_weight) * chunk.score + distance_weight * graph_score
        scored.append((combined, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]
```

## Notes

- The backend is intentionally modular: each retriever and the graph repository can be tested and replaced independently.
- The `RetrievedChunk` model is shared across vector and graph sources so the API response shape is consistent.
