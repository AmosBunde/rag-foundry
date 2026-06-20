import json
from typing import Any

from app.agents.state import AgentState
from app.config import settings
from app.llm import LLMClient

PLANNER_SYSTEM = """You are a medical AI planner. Given a user question and optional patient context, produce a concise step-by-step plan to answer it safely.

Output ONLY a JSON object with this shape:
{
  "plan": ["step 1", "step 2", ...],
  "retrieval_query": "rephrased query for searching medical records and guidelines"
}

Do not provide diagnosis or treatment advice in the plan."""


async def planner_node(state: AgentState, llm: LLMClient | None = None) -> dict[str, Any]:
    llm = llm or LLMClient()
    query = state.get("query", "")
    patient_id = state.get("patient_id")

    prompt = f"User question: {query}\n"
    if patient_id:
        prompt += f"Patient ID: {patient_id}\n"
    prompt += "Create a plan and a retrieval query."

    response = await llm.generate(prompt, system=PLANNER_SYSTEM, temperature=0.1)

    try:
        parsed = json.loads(response.strip())
    except json.JSONDecodeError:
        # Fallback: attempt to extract JSON from markdown fences
        cleaned = response.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[-1].split("```")[0]
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[-1].split("```")[0]
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            parsed = {"plan": ["Analyze question", "Retrieve relevant records", "Verify safety", "Generate educational response"], "retrieval_query": query}

    plan = parsed.get("plan") or ["Analyze question", "Retrieve records", "Verify safety", "Respond"]
    retrieval_query = parsed.get("retrieval_query") or query

    reasoning = state.get("reasoning", [])
    reasoning.append({"agent": "planner", "step": "created_plan", "detail": {"plan": plan, "retrieval_query": retrieval_query}})

    return {
        "plan": plan,
        "retrieval_query": retrieval_query,
        "reasoning": reasoning,
    }
