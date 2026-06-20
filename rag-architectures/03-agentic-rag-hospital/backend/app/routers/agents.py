from fastapi import APIRouter, Depends

from app.agents.graph import build_agent_graph
from app.auth import User, get_current_user
from app.models import AgentStatusResponse

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


@router.get("/status", response_model=AgentStatusResponse)
async def agents_status(user: User = Depends(get_current_user)) -> AgentStatusResponse:
    graph = build_agent_graph()
    nodes = list(graph.get_graph().nodes.keys()) if hasattr(graph, "get_graph") else ["planner", "retriever", "verifier", "responder"]
    return AgentStatusResponse(
        agents={node: "healthy" for node in nodes},
        ready=True,
    )
