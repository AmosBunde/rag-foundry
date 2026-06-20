import time
from typing import Any

from app.agents.graph import build_agent_graph
from app.config import settings
from app.models import AgentQueryResponse, ReasoningStep, RetrievedChunk


class AgentService:
    """Service wrapper around the LangGraph agent workflow."""

    def __init__(self, graph: Any | None = None) -> None:
        self.graph = graph or build_agent_graph()

    async def query(
        self,
        query: str,
        patient_id: str | None = None,
        top_k: int | None = None,
    ) -> AgentQueryResponse:
        top_k = top_k or settings.default_top_k
        start = time.perf_counter()

        initial_state = {
            "query": query,
            "patient_id": patient_id,
            "reasoning": [],
        }
        result = await self.graph.ainvoke(initial_state)

        sources = [RetrievedChunk(**s) for s in result.get("sources", [])]
        reasoning = [ReasoningStep(**r) for r in result.get("reasoning", [])]
        plan = result.get("plan", [])

        latency_ms = (time.perf_counter() - start) * 1000

        return AgentQueryResponse(
            query=query,
            answer=result.get("answer", ""),
            plan=plan,
            reasoning=reasoning,
            sources=sources,
            safety_checks_passed=result.get("safety_checks_passed", False),
            disclaimer=result.get("disclaimer", ""),
            latency_ms=latency_ms,
        )
