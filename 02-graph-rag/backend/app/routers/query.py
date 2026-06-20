import time

from fastapi import APIRouter, Depends

from app.auth import User, get_current_user
from app.config import settings
from app.guardrails import guard_query
from app.graph import GraphRepository, extract_entities
from app.models import GraphQueryRequest, QueryResponse, RetrievedChunk
from app.retrieval.dense import DenseRetriever
from app.retrieval.ranker import rank_by_graph_distance

router = APIRouter(prefix="/api/v1/query", tags=["query"])


def _get_dense() -> DenseRetriever:
    return DenseRetriever()


def _get_graph() -> GraphRepository:
    return GraphRepository()


@router.post("/graph", response_model=QueryResponse)
async def graph_query(
    request: GraphQueryRequest,
    user: User = Depends(get_current_user),
    dense: DenseRetriever = Depends(_get_dense),
    graph: GraphRepository = Depends(_get_graph),
) -> QueryResponse:
    guard_query(request.query)
    start = time.perf_counter()

    # Extract entities from the query using the same lightweight extractor.
    query_entities = extract_entities(request.query, chunk_id="query", max_entities=settings.max_entities_per_chunk)
    entity_ids = [e["id"] for e in query_entities]

    # Retrieve vector candidates from Qdrant.
    vector_results: list[RetrievedChunk] = await dense.search(request.query, top_k=request.top_k * 2)

    # Augment with graph proximity when entities were found.
    graph_distances: dict[str, int] = {}
    if entity_ids:
        graph_distances = await graph.get_chunk_ids_near_entities(
            entity_ids,
            depth=request.graph_depth,
        )

    if graph_distances and vector_results:
        results = rank_by_graph_distance(
            vector_results,
            graph_distances,
            top_k=request.top_k,
        )
    elif graph_distances:
        # No vector results but graph found chunks: rank purely by distance.
        chunk_records = await graph.get_chunks_by_ids(list(graph_distances.keys()))
        results = [
            RetrievedChunk(
                id=record["id"],
                text=record["text"],
                score=1.0 / (1.0 + graph_distances[record["id"]]),
                metadata={"chunk_index": record.get("chunk_index", 0)},
                source="graph",
            )
            for record in chunk_records
        ]
        results.sort(key=lambda c: c.score, reverse=True)
        results = results[: request.top_k]
    else:
        results = vector_results[: request.top_k]

    latency_ms = (time.perf_counter() - start) * 1000
    return QueryResponse(query=request.query, results=results, latency_ms=latency_ms)
