import pytest

from app.services.feedback import FeedbackStore


@pytest.mark.asyncio
async def test_store_feedback() -> None:
    store = FeedbackStore()
    feedback_id = await store.store("q-1", "r-1", True, "Great result")
    assert feedback_id


@pytest.mark.asyncio
async def test_get_feedback_for_result() -> None:
    store = FeedbackStore()
    await store.store("q-1", "r-1", True, None)
    await store.store("q-2", "r-1", False, None)
    results = await store.get_feedback_for_result("r-1")
    assert len(results) == 2


@pytest.mark.asyncio
async def test_feedback_score_positive() -> None:
    store = FeedbackStore()
    await store.store("q-1", "r-1", True, None)
    await store.store("q-2", "r-1", True, None)
    score = await store.get_score("r-1")
    assert score == 1.0


@pytest.mark.asyncio
async def test_feedback_score_negative() -> None:
    store = FeedbackStore()
    await store.store("q-1", "r-1", False, None)
    score = await store.get_score("r-1")
    assert score == -1.0


@pytest.mark.asyncio
async def test_feedback_score_neutral() -> None:
    store = FeedbackStore()
    await store.store("q-1", "r-1", True, None)
    await store.store("q-2", "r-1", False, None)
    score = await store.get_score("r-1")
    assert score == 0.0
