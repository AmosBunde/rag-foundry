import time

from fastapi import APIRouter, Depends

from app.auth import User, get_current_user
from app.config import settings
from app.guardrails import guard_query
from app.ingestion import IngestionService
from app.models import (
    DenseRequest,
    QueryRequest,
    QueryResponse,
    RetrievedChunk,
    SparseRequest,
)
from app.retrieval.dense import DenseRetriever
from app.retrieval.fusion import reciprocal_rank_fusion
from app.retrieval.sparse import SparseRetriever

router = APIRouter(prefix="/api/v1/query", tags=["query"])


def _get_dense() -> DenseRetriever:
    return DenseRetriever()


def _get_sparse() -> SparseRetriever:
    return SparseRetriever()


def _get_ingestion() -> IngestionService:
    return IngestionService()


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
