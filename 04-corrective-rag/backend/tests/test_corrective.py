from unittest.mock import AsyncMock, MagicMock

import pytest

from app.config import settings
from app.models import QueryRequest, RetrievedChunk
from app.services.corrective import CorrectiveRAGService


@pytest.fixture
def mock_service() -> CorrectiveRAGService:
    dense = MagicMock()
    sparse = MagicMock()
    llm = MagicMock()
    feedback = MagicMock()
    return CorrectiveRAGService(dense=dense, sparse=sparse, llm=llm, feedback=feedback)


@pytest.mark.asyncio
async def test_corrective_single_iteration(mock_service: CorrectiveRAGService) -> None:
    mock_service.dense.search = AsyncMock(return_value=[
        RetrievedChunk(id="d1", text="dense", score=0.9, metadata={}, source="dense"),
    ])
    mock_service.sparse.search = AsyncMock(return_value=[])
    mock_service.feedback.get_score = AsyncMock(return_value=0.0)
    mock_service.llm.evaluate_relevance = AsyncMock(return_value=(0.9, "Very relevant"))
    mock_service.llm.generate_answer = AsyncMock(return_value="Answer")

    request = QueryRequest(query="What is RAG?", top_k=1)
    response = await mock_service.query(request)

    assert response.final_confidence == 0.9
    assert len(response.iterations) == 1
    assert response.rewrite_count == 0
    assert response.answer == "Answer"


@pytest.mark.asyncio
async def test_corrective_triggers_rewrite(mock_service: CorrectiveRAGService) -> None:
    mock_service.dense.search = AsyncMock(return_value=[
        RetrievedChunk(id="d1", text="dense", score=0.6, metadata={}, source="dense"),
    ])
    mock_service.sparse.search = AsyncMock(return_value=[])
    mock_service.feedback.get_score = AsyncMock(return_value=0.0)
    mock_service.llm.evaluate_relevance = AsyncMock(side_effect=[
        (0.5, "Low"),
        (0.85, "Good"),
    ])
    mock_service.llm.rewrite_query = AsyncMock(return_value="What is retrieval augmented generation?")
    mock_service.llm.generate_answer = AsyncMock(return_value="Better answer")

    request = QueryRequest(query="RAG?", top_k=1)
    response = await mock_service.query(request)

    assert response.rewrite_count == 1
    assert response.final_confidence == 0.85
    assert len(response.iterations) == 2


@pytest.mark.asyncio
async def test_corrective_exhausts_iterations(mock_service: CorrectiveRAGService) -> None:
    mock_service.dense.search = AsyncMock(return_value=[
        RetrievedChunk(id="d1", text="dense", score=0.4, metadata={}, source="dense"),
    ])
    mock_service.sparse.search = AsyncMock(return_value=[])
    mock_service.feedback.get_score = AsyncMock(return_value=0.0)
    mock_service.llm.evaluate_relevance = AsyncMock(return_value=(0.4, "Still low"))
    mock_service.llm.rewrite_query = AsyncMock(return_value="Rewritten query")
    mock_service.llm.generate_answer = AsyncMock(return_value="Best effort answer")

    request = QueryRequest(query="RAG?", top_k=1)
    response = await mock_service.query(request)

    assert len(response.iterations) == settings.max_corrective_iterations
    assert response.rewrite_count == settings.max_corrective_iterations - 1


@pytest.mark.asyncio
async def test_feedback_boost(mock_service: CorrectiveRAGService) -> None:
    results = [
        RetrievedChunk(id="r1", text="a", score=0.5, metadata={}, source="dense"),
        RetrievedChunk(id="r2", text="b", score=0.5, metadata={}, source="sparse"),
    ]
    mock_service.feedback.get_score = AsyncMock(side_effect=[1.0, -1.0])
    boosted = await mock_service._apply_feedback_boost(results)
    assert boosted[0].score > boosted[1].score
