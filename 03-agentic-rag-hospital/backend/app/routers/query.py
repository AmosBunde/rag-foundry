import time

from fastapi import APIRouter, Depends

from app.agents.service import AgentService
from app.auth import User, get_current_user
from app.guardrails import guard_query
from app.models import AgentQueryRequest, AgentQueryResponse

router = APIRouter(prefix="/api/v1/query", tags=["query"])


def _get_agent_service() -> AgentService:
    return AgentService()


@router.post("/agent", response_model=AgentQueryResponse)
async def agent_query(
    request: AgentQueryRequest,
    user: User = Depends(get_current_user),
    service: AgentService = Depends(_get_agent_service),
) -> AgentQueryResponse:
    guard_query(request.query)
    start = time.perf_counter()
    response = await service.query(
        query=request.query,
        patient_id=request.patient_id,
        top_k=request.top_k,
    )
    response.latency_ms = (time.perf_counter() - start) * 1000
    return response
