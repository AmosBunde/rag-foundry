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
async def test_caption_image() -> None:
    client = LLMClient()
    route = respx.post(f"{client.url}/api/generate").mock(return_value=Response(200, json={"response": "A cat"}))
    result = await client.caption_image()
    assert result == "A cat"
    assert route.called


@pytest.mark.asyncio
@respx.mock
async def test_transcribe_audio() -> None:
    client = LLMClient()
    route = respx.post(f"{client.url}/api/generate").mock(return_value=Response(200, json={"response": "hello world"}))
    result = await client.transcribe_audio(b"audio")
    assert result == "hello world"
    assert route.called
