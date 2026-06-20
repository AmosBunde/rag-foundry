import respx
from httpx import Response

from app.llm import LLMClient


@respx.mock
async def test_llm_generate() -> None:
    route = respx.post("http://localhost:11434/api/generate").mock(
        return_value=Response(200, json={"response": "Hello"})
    )

    client = LLMClient()
    result = await client.generate("Say hello")

    assert result == "Hello"
    assert route.called
