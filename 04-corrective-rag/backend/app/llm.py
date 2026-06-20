import json
import re

import httpx

from app.config import settings


class LLMClient:
    """Minimal LLM client wrapping Ollama for local development."""

    def __init__(self) -> None:
        self.url = settings.ollama_url
        self.model = settings.llm_model

    async def generate(self, prompt: str, system: str | None = None, temperature: float = 0.2) -> str:
        payload: dict = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.url}/api/generate",
                json=payload,
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")

    async def rewrite_query(self, query: str, iteration: int) -> str:
        """Rewrite a query to improve retrieval coverage."""
        system = (
            "You are a query-rewriting assistant for a retrieval system. "
            "Rewrite the user's query to make it more specific and retrieval-friendly. "
            "Return ONLY the rewritten query, with no preamble or explanation."
        )
        prompt = (
            f"Original query: {query}\n"
            f"This is rewrite attempt {iteration}. "
            "Produce a clearer, more explicit version of the query that preserves intent."
        )
        rewritten = (await self.generate(prompt, system=system, temperature=0.3)).strip()
        # Remove surrounding quotes if the model added them.
        if rewritten.startswith('"') and rewritten.endswith('"'):
            rewritten = rewritten[1:-1]
        return rewritten or query

    async def evaluate_relevance(self, query: str, chunks: list[dict]) -> tuple[float, str]:
        """Evaluate answer relevance and return a confidence score in [0, 1]."""
        if not chunks:
            return 0.0, "No retrieved context."

        context = "\n\n".join(f"[{i+1}] {c['text']}" for i, c in enumerate(chunks))
        system = (
            "You are a strict relevance evaluator. Given a query and retrieved passages, "
            "respond with a JSON object containing exactly two keys: "
            "'confidence' (a float between 0.0 and 1.0) and 'reason' (a short sentence). "
            "Base confidence on whether the passages together contain enough information "
            "to answer the query accurately."
        )
        prompt = (
            f"Query: {query}\n\n"
            f"Retrieved passages:\n{context}\n\n"
            "Evaluate relevance. Return only JSON."
        )
        raw = await self.generate(prompt, system=system, temperature=0.1)
        return self._parse_confidence(raw)

    def _parse_confidence(self, text: str) -> tuple[float, str]:
        """Best-effort parse of JSON confidence from LLM output."""
        try:
            # Try to find a JSON object in case the model added markdown fences.
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                text = match.group(0)
            data = json.loads(text)
            confidence = float(data.get("confidence", 0.0))
            reason = str(data.get("reason", "No reason provided."))
            return max(0.0, min(1.0, confidence)), reason
        except Exception:
            pass

        # Fallback: scan for a number near keywords.
        match = re.search(r"(confidence|score)\s*[:=]?\s*is?\s*([0-9]*\.?[0-9]+)", text, re.IGNORECASE)
        if match:
            return max(0.0, min(1.0, float(match.group(2)))), text.strip()
        return 0.5, text.strip()

    async def generate_answer(self, query: str, chunks: list[dict]) -> str:
        """Generate a concise answer from retrieved chunks."""
        if not chunks:
            return "I could not find relevant information to answer your question."

        context = "\n\n".join(f"[{i+1}] {c['text']}" for i, c in enumerate(chunks))
        system = (
            "You are a helpful assistant. Answer the user's question using only the provided context. "
            "If the context does not contain enough information, say so."
        )
        prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer concisely."
        return (await self.generate(prompt, system=system, temperature=0.2)).strip()
