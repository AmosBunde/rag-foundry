import time

from fastapi import APIRouter, Depends

from app.auth import User, get_current_user
from app.guardrails import guard_query
from app.models import MultimodalQueryRequest, MultimodalQueryResponse
from app.retrieval.multimodal import MultimodalRetriever

router = APIRouter(prefix="/api/v1/query", tags=["query"])


def _get_retriever() -> MultimodalRetriever:
    return MultimodalRetriever()


@router.post("/multimodal", response_model=MultimodalQueryResponse)
async def multimodal_query(
    request: MultimodalQueryRequest,
    user: User = Depends(get_current_user),
    retriever: MultimodalRetriever = Depends(_get_retriever),
) -> MultimodalQueryResponse:
    guard_query(request.query)
    start = time.perf_counter()
    results = await retriever.search(request.query, top_k=request.top_k, modalities=request.modalities)
    latency_ms = (time.perf_counter() - start) * 1000
    return MultimodalQueryResponse(
        query=request.query,
        results=results,
        latency_ms=latency_ms,
        modalities=request.modalities,
    )
