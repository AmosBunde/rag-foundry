from typing import Annotated, Any, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):
    """Shared state passed between agent nodes in the medical QA graph."""

    messages: Annotated[list, add_messages]
    query: str
    patient_id: str | None
    plan: list[str]
    retrieval_query: str
    sources: list[dict[str, Any]]
    verification: dict[str, Any]
    answer: str
    safety_checks_passed: bool
    disclaimer: str
    reasoning: list[dict[str, Any]]
    error: str | None
