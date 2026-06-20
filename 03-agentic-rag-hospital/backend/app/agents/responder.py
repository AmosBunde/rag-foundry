from typing import Any

from app.agents.state import AgentState
from app.config import settings
from app.guardrails import append_medical_disclaimer
from app.llm import LLMClient

RESPONDER_SYSTEM = """You are a helpful medical information assistant. Answer the user's question using ONLY the retrieved sources.

Rules:
- Do not diagnose, prescribe, or provide personal treatment advice.
- If the sources do not contain relevant information, say you cannot answer.
- Keep answers concise and cite the source IDs when possible.
- Include a disclaimer that this is not medical advice."""


async def responder_node(state: AgentState, llm: LLMClient | None = None) -> dict[str, Any]:
    llm = llm or LLMClient()
    query = state.get("query", "")
    sources = state.get("sources", [])
    verification = state.get("verification", {})

    if not verification.get("safe_to_answer", True):
        answer = (
            "I'm unable to answer this question. It may request personal medical advice, "
            "contain unsafe content, or fall outside the scope of the available records. "
            "Please consult a qualified healthcare provider."
        )
        reasoning = state.get("reasoning", [])
        reasoning.append({"agent": "responder", "step": "refused_unsafe", "detail": {"concerns": verification.get("concerns", [])}})
        return {
            "answer": answer,
            "safety_checks_passed": False,
            "disclaimer": "",
            "reasoning": reasoning,
        }

    prompt = f"User question: {query}\n\nRetrieved sources:\n"
    for source in sources[:5]:
        prompt += f"- [{source.get('id')}] {source.get('text')}\n"
    prompt += "\nProvide a safe, educational answer."

    answer = await llm.generate(prompt, system=RESPONDER_SYSTEM, temperature=0.2)

    disclaimer = ""
    if verification.get("needs_disclaimer") or settings.require_medical_disclaimer:
        answer = append_medical_disclaimer(answer)
        disclaimer = "Medical advice disclaimer appended."

    reasoning = state.get("reasoning", [])
    reasoning.append({"agent": "responder", "step": "generated_answer", "detail": {"length": len(answer), "cited_sources": [s.get("id") for s in sources[:5]]}})

    return {
        "answer": answer,
        "safety_checks_passed": True,
        "disclaimer": disclaimer,
        "reasoning": reasoning,
    }
