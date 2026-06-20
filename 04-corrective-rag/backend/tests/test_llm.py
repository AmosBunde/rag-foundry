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
async def test_rewrite_query() -> None:
    client = LLMClient()
    respx.post(f"{client.url}/api/generate").mock(
        return_value=Response(200, json={"response": "\"What is RAG?\""})
    )
    result = await client.rewrite_query("rag", iteration=1)
    assert "RAG" in result


@pytest.mark.asyncio
@respx.mock
async def test_evaluate_relevance() -> None:
    client = LLMClient()
    respx.post(f"{client.url}/api/generate").mock(
        return_value=Response(200, json={"response": '{"confidence": 0.82, "reason": "Relevant."}'})
    )
    confidence, reason = await client.evaluate_relevance("What is RAG?", [{"id": "1", "text": "RAG is retrieval augmented generation."}])
    assert confidence == 0.82
    assert "Relevant" in reason


@pytest.mark.asyncio
@respx.mock
async def test_evaluate_relevance_fallback() -> None:
    client = LLMClient()
    respx.post(f"{client.url}/api/generate").mock(
        return_value=Response(200, json={"response": "The confidence score is 0.6 because it is okay."})
    )
    confidence, _ = await client.evaluate_relevance("What is RAG?", [{"id": "1", "text": "RAG is retrieval augmented generation."}])
    assert confidence == 0.6


@pytest.mark.asyncio
@respx.mock
async def test_generate_answer() -> None:
    client = LLMClient()
    respx.post(f"{client.url}/api/generate").mock(
        return_value=Response(200, json={"response": "It is a technique."})
    )
    answer = await client.generate_answer("What is RAG?", [{"id": "1", "text": "RAG is retrieval augmented generation."}])
    assert "technique" in answer


@pytest.mark.asyncio
async def test_generate_answer_no_chunks() -> None:
    client = LLMClient()
    answer = await client.generate_answer("What is RAG?", [])
    assert "could not find" in answer.lower()
