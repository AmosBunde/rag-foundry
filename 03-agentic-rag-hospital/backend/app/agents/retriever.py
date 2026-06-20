from typing import Any

from app.agents.state import AgentState
from app.config import settings
from app.retrieval.dense import DenseRetriever
from app.retrieval.fusion import reciprocal_rank_fusion
from app.retrieval.sparse import SparseRetriever


async def retriever_node(
    state: AgentState,
    dense: DenseRetriever | None = None,
    sparse: SparseRetriever | None = None,
    top_k: int | None = None,
) -> dict[str, Any]:
    dense = dense or DenseRetriever()
    sparse = sparse or SparseRetriever()
    top_k = top_k or settings.default_top_k

    retrieval_query = state.get("retrieval_query") or state.get("query", "")
    patient_id = state.get("patient_id")

    dense_results = await dense.search(retrieval_query, top_k)
    sparse_results = await sparse.search(retrieval_query, top_k)

    if dense_results and sparse_results:
        sources = reciprocal_rank_fusion(dense_results, sparse_results, top_k=top_k)
    elif dense_results:
        sources = dense_results[:top_k]
    elif sparse_results:
        sources = sparse_results[:top_k]
    else:
        sources = []

    # Boost sources that mention the patient_id in metadata
    if patient_id:
        sources.sort(key=lambda s: (s.metadata.get("patient_id") == patient_id, s.score), reverse=True)

    reasoning = state.get("reasoning", [])
    reasoning.append({
        "agent": "retriever",
        "step": "retrieved_sources",
        "detail": {"query": retrieval_query, "count": len(sources)},
    })

    return {
        "sources": [s.model_dump() for s in sources],
        "reasoning": reasoning,
    }
