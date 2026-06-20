from datetime import timedelta

import httpx
from fastapi import APIRouter, Response

from app.config import settings
from app.graph import GraphRepository
from app.models import HealthResponse, ReadyResponse
from app.observability import render_metrics

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@router.get("/ready", response_model=ReadyResponse)
async def ready() -> ReadyResponse:
    checks: dict[str, bool] = {}

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{settings.qdrant_url}/healthz", timeout=timedelta(seconds=2).total_seconds())
            checks["qdrant"] = r.status_code == 200
    except Exception:
        checks["qdrant"] = False

    try:
        graph = GraphRepository()
        checks["neo4j"] = await graph.ready()
    except Exception:
        checks["neo4j"] = False

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{settings.ollama_url}/api/tags", timeout=timedelta(seconds=2).total_seconds())
            checks["ollama"] = r.status_code == 200
    except Exception:
        checks["ollama"] = False

    all_ready = all(checks.values())
    return ReadyResponse(ready=all_ready, checks=checks)


@router.get("/metrics")
async def metrics() -> Response:
    data, content_type = render_metrics()
    return Response(content=data, media_type=content_type)
