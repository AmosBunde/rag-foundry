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
