import pytest
import respx
from httpx import Response

from app.llm import LLMClient


@pytest.mark.asyncio
@respx.mock
async def test_llm_generate() -> None:
    client = LLMClient()
    route = respx.post(f"{client.url}/api/generate").mock(return_value=Response(200, json={"response": "hello"}))
    result = await client.generate("say hi")
    assert result == "hello"
    assert route.called


@pytest.mark.asyncio
@respx.mock
async def test_llm_embed() -> None:
    client = LLMClient()
    route = respx.post(f"{client.url}/api/embeddings").mock(return_value=Response(200, json={"embedding": [0.1, 0.2, 0.3]}))
    result = await client.embed(["hello"])
    assert len(result) == 1
    assert result[0] == [0.1, 0.2, 0.3]
    assert route.called
