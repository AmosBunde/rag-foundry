import json
from typing import Any

from app.agents.state import AgentState
from app.config import settings
from app.guardrails import requires_medical_disclaimer, validate_query
from app.llm import LLMClient

VERIFIER_SYSTEM = """You are a medical safety verifier. Review the retrieved sources and the user's question.

Output ONLY a JSON object:
{
  "safe_to_answer": true|false,
  "concerns": ["concern 1", ...],
  "allowed_topics": ["topic covered by sources"],
  "recommended_answer_type": "factual summary | educational information | refusal"
}

Flag requests that ask for personal diagnosis, prescription, or treatment planning."""


async def verifier_node(state: AgentState, llm: LLMClient | None = None) -> dict[str, Any]:
    llm = llm or LLMClient()
    query = state.get("query", "")
    sources = state.get("sources", [])

    guardrail = validate_query(query)

    prompt = f"User question: {query}\nRetrieved sources:\n"
    for idx, source in enumerate(sources[:5], start=1):
        prompt += f"{idx}. {source.get('text', '')}\n"
    prompt += "\nAssess safety and coverage."

    response = await llm.generate(prompt, system=VERIFIER_SYSTEM, temperature=0.1)

    try:
        parsed = json.loads(response.strip())
    except json.JSONDecodeError:
        cleaned = response.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[-1].split("```")[0]
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[-1].split("```")[0]
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            parsed = {"safe_to_answer": True, "concerns": [], "allowed_topics": [], "recommended_answer_type": "educational information"}

    safe_to_answer = bool(parsed.get("safe_to_answer", True))
    concerns = parsed.get("concerns", []) or []

    # If guardrails already blocked, force unsafe
    if not guardrail.allowed:
        safe_to_answer = False
        concerns.extend(guardrail.violations)

    needs_disclaimer = requires_medical_disclaimer(query)

    reasoning = state.get("reasoning", [])
    reasoning.append({
        "agent": "verifier",
        "step": "verified_safety",
        "detail": {
            "safe_to_answer": safe_to_answer,
            "concerns": concerns,
            "needs_disclaimer": needs_disclaimer,
            "guardrail_allowed": guardrail.allowed,
        },
    })

    return {
        "verification": {
            "safe_to_answer": safe_to_answer,
            "concerns": concerns,
            "allowed_topics": parsed.get("allowed_topics", []),
            "recommended_answer_type": parsed.get("recommended_answer_type", "educational information"),
            "needs_disclaimer": needs_disclaimer,
        },
        "reasoning": reasoning,
    }
