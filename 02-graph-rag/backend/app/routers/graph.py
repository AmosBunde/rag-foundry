from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth import User, get_current_user
from app.graph import GraphRepository
from app.models import EntityResponse, ExpandResponse, RetrievedChunk

router = APIRouter(prefix="/api/v1/graph", tags=["graph"])


def _get_graph() -> GraphRepository:
    return GraphRepository()


@router.get("/entities", response_model=list[EntityResponse])
async def list_entities(
    name: str | None = Query(None, description="Optional substring filter on entity name"),
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(get_current_user),
    graph: GraphRepository = Depends(_get_graph),
) -> list[EntityResponse]:
    records = await graph.get_entities(name_query=name, limit=limit)
    return [
        EntityResponse(
            id=record["id"],
            name=record["name"],
            label=record.get("label", "Entity"),
        )
        for record in records
    ]


@router.get("/expand/{entity_id}", response_model=ExpandResponse)
async def expand_entity(
    entity_id: str,
    depth: int = Query(1, ge=1, le=3),
    user: User = Depends(get_current_user),
    graph: GraphRepository = Depends(_get_graph),
) -> ExpandResponse:
    data = await graph.expand_entity(entity_id, depth=depth)
    if data is None:
        raise HTTPException(status_code=404, detail="Entity not found")

    related = [
        EntityResponse(id=r["id"], name=r["name"], label=r.get("label", "Entity"))
        for r in data.get("related", [])
    ]

    # Pull the chunks that mention this entity
    chunk_records = await graph.get_chunks_by_ids([])  # placeholder; hydrated from related graph if needed
    # A fuller implementation would traverse (:Chunk)-[:MENTIONS]->(e) here.
    chunks: list[RetrievedChunk] = []

    return ExpandResponse(
        entity=EntityResponse(id=data["id"], name=data["name"], label=data.get("label", "Entity")),
        related_entities=related,
        chunks=chunks,
    )
