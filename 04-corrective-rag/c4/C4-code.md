# C4 — Code Diagram: Corrective RAG Backend

This diagram zooms into the key classes and functions that implement corrective retrieval, feedback, and ingestion.

```mermaid
classDiagram
    class FastAPI {
        +lifespan
        +include_router()
    }

    class QueryRouter {
        +corrective_query(request: QueryRequest)
        +submit_feedback(request: FeedbackRequest)
        +hybrid_query(request: QueryRequest)
        +dense_query(request: DenseRequest)
        +sparse_query(request: SparseRequest)
    }

    class IngestRouter {
        +ingest_documents(request: IngestRequest)
    }

    class CorrectiveRAGService {
        -dense: DenseRetriever
        -sparse: SparseRetriever
        -llm: LLMClient
        -feedback: FeedbackStore
        -confidence_threshold: float
        -max_iterations: int
        +query(request: QueryRequest) CorrectiveResponse
        +submit_feedback(query_id, result_id, helpful, comment) str
        -_retrieve(query, top_k, use_dense, use_sparse) list[RetrievedChunk]
        -_score_confidence(query, results) float
        -_apply_feedback_boost(results) list[RetrievedChunk]
    }

    class FeedbackStore {
        -_memory: list[dict]
        +store(query_id, result_id, helpful, comment) str
        +get_score(result_id) float
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

    class SparseRetriever {
        -client: Elasticsearch
        -index: str
        +upsert(documents) int
        +search(query: str, top_k: int) list[RetrievedChunk]
    }

    class LLMClient {
        -url: str
        -model: str
        +generate(prompt, system, temperature) str
        +rewrite_query(query, iteration) str
        +evaluate_relevance(query, chunks) tuple[float, str]
        +generate_answer(query, chunks) str
    }

    class IngestionService {
        -dense: DenseRetriever
        -sparse: SparseRetriever
        +ingest(documents) IngestResponse
        -_chunk_text(text, chunk_size, overlap) list[str]
    }

    class reciprocal_rank_fusion {
        +reciprocal_rank_fusion(dense, sparse, k, top_k) list[RetrievedChunk]
    }

    class Guardrails {
        +validate_query(text, max_length, use_presidio) GuardrailResult
        +validate_metadata(metadata) GuardrailResult
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

    class CorrectiveResponse {
        +query: str
        +original_query: str
        +iterations: list[CorrectiveIteration]
        +final_results: list[RetrievedChunk]
        +final_confidence: float
        +answer: str
        +latency_ms: float
        +rewrite_count: int
    }

    FastAPI --> QueryRouter
    FastAPI --> IngestRouter
    QueryRouter --> CorrectiveRAGService
    QueryRouter --> FeedbackStore
    QueryRouter --> DenseRetriever
    QueryRouter --> SparseRetriever
    QueryRouter --> reciprocal_rank_fusion
    QueryRouter --> Guardrails
    IngestRouter --> IngestionService
    IngestionService --> DenseRetriever
    IngestionService --> SparseRetriever
    CorrectiveRAGService --> DenseRetriever
    CorrectiveRAGService --> SparseRetriever
    CorrectiveRAGService --> LLMClient
    CorrectiveRAGService --> FeedbackStore
    CorrectiveRAGService ..> CorrectiveResponse
    DenseRetriever ..> RetrievedChunk
    SparseRetriever ..> RetrievedChunk
    reciprocal_rank_fusion ..> RetrievedChunk
    QueryRouter --> Auth
    IngestRouter --> Auth
```

## Key Code Paths

### Corrective query

```python
# app/routers/query.py
@router.post("/corrective", response_model=CorrectiveResponse)
async def corrective_query(
    request: QueryRequest,
    user: User = Depends(get_current_user),
    service: CorrectiveRAGService = Depends(_get_corrective_service),
) -> CorrectiveResponse:
    guard_query(request.query)
    response = await service.query(request)
    CORRECTIVE_ITERATIONS.observe(len(response.iterations))
    CONFIDENCE_SCORE.observe(response.final_confidence)
    return response
```

### Confidence-driven loop

```python
# app/services/corrective.py
async def query(self, request: QueryRequest) -> CorrectiveResponse:
    for iteration in range(1, self.max_iterations + 1):
        results = await self._retrieve(current_query, request.top_k, ...)
        results = await self._apply_feedback_boost(results)
        confidence = await self._score_confidence(current_query, results)
        iterations.append(CorrectiveIteration(...))
        if confidence >= self.confidence_threshold:
            break
        if iteration < self.max_iterations:
            current_query = await self.llm.rewrite_query(original_query, iteration)
    answer = await self.llm.generate_answer(original_query, ...)
    return CorrectiveResponse(...)
```

### Relevance evaluation

```python
# app/llm.py
async def evaluate_relevance(self, query: str, chunks: list[dict]) -> tuple[float, str]:
    system = "Respond with JSON containing 'confidence' and 'reason'."
    prompt = f"Query: {query}\n\nPassages: ..."
    raw = await self.generate(prompt, system=system, temperature=0.1)
    return self._parse_confidence(raw)
```

### Feedback boost

```python
# app/services/corrective.py
async def _apply_feedback_boost(self, results: list[RetrievedChunk]) -> list[RetrievedChunk]:
    scored = []
    for r in results:
        feedback_score = await self.feedback.get_score(r.id)
        boosted = r.score + (0.05 * feedback_score)
        scored.append(RetrievedChunk(..., score=max(0.0, boosted)))
    scored.sort(key=lambda x: x.score, reverse=True)
    return scored
```

### Feedback submission

```python
# app/routers/query.py
@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    store: FeedbackStore = Depends(_get_feedback_store),
) -> FeedbackResponse:
    feedback_id = await store.store(request.query_id, request.result_id, request.helpful, request.comment)
    FEEDBACK_COUNT.labels(helpful=str(request.helpful).lower()).inc()
    return FeedbackResponse(stored=True, feedback_id=feedback_id)
```

## Notes

- The backend is intentionally modular: each retriever, the LLM client, and the feedback store can be tested and replaced independently.
- The `CorrectiveRAGService` is designed so the rewrite loop, confidence scorer, and feedback booster are separate, testable methods.
- The `FeedbackStore` uses an in-memory mock by default; replace it with a PostgreSQL/Redis implementation in production.
