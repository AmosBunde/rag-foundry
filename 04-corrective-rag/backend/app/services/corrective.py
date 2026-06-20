import time
import uuid

from app.config import settings
from app.llm import LLMClient
from app.models import CorrectiveIteration, CorrectiveResponse, QueryRequest, RetrievedChunk
from app.retrieval.dense import DenseRetriever
from app.retrieval.fusion import reciprocal_rank_fusion
from app.retrieval.sparse import SparseRetriever
from app.services.feedback import FeedbackStore


class CorrectiveRAGService:
    """Self-correcting retrieval with confidence scoring and feedback-driven re-ranking."""

    def __init__(
        self,
        dense: DenseRetriever | None = None,
        sparse: SparseRetriever | None = None,
        llm: LLMClient | None = None,
        feedback: FeedbackStore | None = None,
    ) -> None:
        self.dense = dense or DenseRetriever()
        self.sparse = sparse or SparseRetriever()
        self.llm = llm or LLMClient()
        self.feedback = feedback or FeedbackStore()
        self.confidence_threshold = settings.confidence_threshold
        self.max_iterations = settings.max_corrective_iterations

    async def _retrieve(self, query: str, top_k: int, use_dense: bool, use_sparse: bool) -> list[RetrievedChunk]:
        dense_results: list[RetrievedChunk] = []
        sparse_results: list[RetrievedChunk] = []

        if use_dense:
            dense_results = await self.dense.search(query, top_k)
        if use_sparse:
            sparse_results = await self.sparse.search(query, top_k)

        if dense_results and sparse_results:
            return reciprocal_rank_fusion(dense_results, sparse_results, top_k=top_k)
        if dense_results:
            return dense_results[:top_k]
        if sparse_results:
            return sparse_results[:top_k]
        return []

    async def _score_confidence(self, query: str, results: list[RetrievedChunk]) -> float:
        chunks = [{"id": r.id, "text": r.text} for r in results]
        confidence, _ = await self.llm.evaluate_relevance(query, chunks)
        return confidence

    async def _apply_feedback_boost(self, results: list[RetrievedChunk]) -> list[RetrievedChunk]:
        if not settings.enable_feedback_rerank:
            return results

        scored = []
        for r in results:
            feedback_score = await self.feedback.get_score(r.id)
            boosted = r.score + (0.05 * feedback_score)
            scored.append(
                RetrievedChunk(
                    id=r.id,
                    text=r.text,
                    score=max(0.0, boosted),
                    metadata={**r.metadata, "feedback_score": feedback_score},
                    source=r.source,
                )
            )
        scored.sort(key=lambda x: x.score, reverse=True)
        return scored

    async def query(self, request: QueryRequest) -> CorrectiveResponse:
        start = time.perf_counter()
        original_query = request.query
        current_query = original_query
        iterations: list[CorrectiveIteration] = []
        rewrite_count = 0

        for iteration in range(1, self.max_iterations + 1):
            results = await self._retrieve(
                current_query,
                request.top_k,
                request.use_dense,
                request.use_sparse,
            )
            results = await self._apply_feedback_boost(results)
            confidence = await self._score_confidence(current_query, results)

            iterations.append(
                CorrectiveIteration(
                    iteration=iteration,
                    query=current_query,
                    results=results,
                    confidence=confidence,
                    rewritten=rewrite_count > 0,
                )
            )

            if confidence >= self.confidence_threshold:
                break

            if iteration < self.max_iterations:
                current_query = await self.llm.rewrite_query(original_query, iteration)
                rewrite_count += 1

        final_results = iterations[-1].results
        final_confidence = iterations[-1].confidence
        answer = await self.llm.generate_answer(original_query, [{"id": r.id, "text": r.text} for r in final_results])
        latency_ms = (time.perf_counter() - start) * 1000

        return CorrectiveResponse(
            query=iterations[-1].query,
            original_query=original_query,
            iterations=iterations,
            final_results=final_results,
            final_confidence=final_confidence,
            answer=answer,
            latency_ms=latency_ms,
            rewrite_count=rewrite_count,
        )

    async def submit_feedback(
        self,
        query_id: str,
        result_id: str,
        helpful: bool,
        comment: str | None,
    ) -> str:
        return await self.feedback.store(query_id, result_id, helpful, comment)


def generate_query_id() -> str:
    return str(uuid.uuid4())
