import time

from fastapi import APIRouter, Depends

from app.auth import User, get_current_user
from app.config import settings
from app.guardrails import guard_query
from app.models import (
    CorrectiveResponse,
    DenseRequest,
    FeedbackRequest,
    FeedbackResponse,
    QueryRequest,
    QueryResponse,
    RetrievedChunk,
    SparseRequest,
)
from app.observability import CONFIDENCE_SCORE, CORRECTIVE_ITERATIONS, FEEDBACK_COUNT
from app.retrieval.dense import DenseRetriever
from app.retrieval.fusion import reciprocal_rank_fusion
from app.retrieval.sparse import SparseRetriever
from app.services.corrective import CorrectiveRAGService
from app.services.feedback import FeedbackStore

router = APIRouter(prefix="/api/v1/query", tags=["query"])


def _get_dense() -> DenseRetriever:
    return DenseRetriever()


def _get_sparse() -> SparseRetriever:
    return SparseRetriever()


def _get_corrective_service() -> CorrectiveRAGService:
    return CorrectiveRAGService()


def _get_feedback_store() -> FeedbackStore:
    return FeedbackStore()


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


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    user: User = Depends(get_current_user),
    store: FeedbackStore = Depends(_get_feedback_store),
) -> FeedbackResponse:
    feedback_id = await store.store(
        request.query_id,
        request.result_id,
        request.helpful,
        request.comment,
    )
    FEEDBACK_COUNT.labels(helpful=str(request.helpful).lower()).inc()
    return FeedbackResponse(stored=True, feedback_id=feedback_id)


@router.post("/hybrid", response_model=QueryResponse)
async def hybrid_query(
    request: QueryRequest,
    user: User = Depends(get_current_user),
    dense: DenseRetriever = Depends(_get_dense),
    sparse: SparseRetriever = Depends(_get_sparse),
) -> QueryResponse:
    guard_query(request.query)
    start = time.perf_counter()

    dense_results: list[RetrievedChunk] = []
    sparse_results: list[RetrievedChunk] = []

    if request.use_dense:
        dense_results = await dense.search(request.query, request.top_k)
    if request.use_sparse:
        sparse_results = await sparse.search(request.query, request.top_k)

    if dense_results and sparse_results:
        results = reciprocal_rank_fusion(dense_results, sparse_results, top_k=request.top_k)
    elif dense_results:
        results = dense_results[: request.top_k]
    elif sparse_results:
        results = sparse_results[: request.top_k]
    else:
        results = []

    latency_ms = (time.perf_counter() - start) * 1000
    return QueryResponse(query=request.query, results=results, latency_ms=latency_ms)


@router.post("/dense", response_model=list[RetrievedChunk])
async def dense_query(
    request: DenseRequest,
    user: User = Depends(get_current_user),
    dense: DenseRetriever = Depends(_get_dense),
) -> list[RetrievedChunk]:
    guard_query(request.query)
    return await dense.search(request.query, request.top_k)


@router.post("/sparse", response_model=list[RetrievedChunk])
async def sparse_query(
    request: SparseRequest,
    user: User = Depends(get_current_user),
    sparse: SparseRetriever = Depends(_get_sparse),
) -> list[RetrievedChunk]:
    guard_query(request.query)
    return await sparse.search(request.query, request.top_k)
