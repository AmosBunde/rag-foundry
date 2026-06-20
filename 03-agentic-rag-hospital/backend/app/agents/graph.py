from typing import Any

from langgraph.graph import END, StateGraph

from app.agents.planner import planner_node
from app.agents.responder import responder_node
from app.agents.retriever import retriever_node
from app.agents.state import AgentState
from app.agents.verifier import verifier_node


def _should_respond(state: AgentState) -> str:
    # Always route to responder; responder decides whether to refuse.
    return "responder"


def build_agent_graph() -> StateGraph:
    """Build and return the compiled LangGraph agent graph."""
    workflow = StateGraph(AgentState)

    workflow.add_node("planner", planner_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("verifier", verifier_node)
    workflow.add_node("responder", responder_node)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "retriever")
    workflow.add_edge("retriever", "verifier")
    workflow.add_conditional_edges("verifier", _should_respond, {"responder": "responder"})
    workflow.add_edge("responder", END)

    return workflow.compile()


async def run_agent_graph(query: str, patient_id: str | None = None, top_k: int = 5, **kwargs: Any) -> dict[str, Any]:
    """Convenience helper to invoke the compiled graph with initial state."""
    graph = build_agent_graph()
    initial_state: AgentState = {
        "query": query,
        "patient_id": patient_id,
        "reasoning": [],
    }
    result = await graph.ainvoke(initial_state)
    return result
