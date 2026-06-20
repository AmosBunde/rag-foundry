# ADR 005: Corrective Retrieval and Feedback Strategy

## Status

Accepted

## Context

Standard retrieval can return low-confidence context that does not answer the user's question. The Corrective RAG architecture must automatically detect poor retrieval, attempt to improve it, and learn from user feedback over time.

## Decision

Implement a **self-correcting retrieval loop** with the following components:

1. **Confidence scoring**: After each retrieval, an LLM evaluates whether the retrieved passages contain enough information to answer the query. The LLM returns a score in `[0, 1]` and a short reason.
2. **Rewrite and re-retrieve**: If confidence is below `CONFIDENCE_THRESHOLD` (default `0.75`) and fewer than `MAX_CORRECTIVE_ITERATIONS` (default `3`) iterations have run, the original query is rewritten to be more explicit and retrieval-friendly, then re-run.
3. **Feedback-driven re-ranking**: User feedback (thumbs-up / thumbs-down) is stored in a mock Postgres/Redis layer. Each chunk receives a feedback score in `[-1, 1]` which is applied as a small boost or penalty to its retrieval score.
4. **Iteration transparency**: The `/api/v1/query/corrective` endpoint returns every iteration (query, results, confidence, rewritten flag) so the frontend can display the reasoning chain.

## Consequences

- Positive: Iterative rewriting can recover from ambiguous or overly narrow queries.
- Positive: Feedback scores improve result ranking without retraining the embedding model.
- Positive: Exposing iterations builds user trust and simplifies debugging.
- Negative: Each LLM evaluation adds latency; the loop can call the LLM up to `MAX_CORRECTIVE_ITERATIONS + 1` times per query.
- Negative: LLM-generated confidence scores are approximate and may not correlate with human judgment without calibration.
- Negative: The feedback store is currently in-memory; production must switch to PostgreSQL and/or Redis.

## Alternatives Considered

- **Single-shot retrieval with reranking only**: simpler but cannot recover from a poor initial query.
- **ReAct / agentic loop with tool use**: more flexible but harder to test and more expensive per query.
- **Embedding-based query expansion**: can improve recall without LLM latency, but does not judge answer relevance.

## References

- [Self-RAG paper, Asai et al.](https://arxiv.org/abs/2310.11511)
- [Corrective RAG (CRAG) paper, Yan et al.](https://arxiv.org/abs/2401.15884)
- [Reciprocal Rank Fusion paper, Cormack et al.](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)
