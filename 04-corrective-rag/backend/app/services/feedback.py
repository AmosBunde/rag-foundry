import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


class FeedbackStore:
    """Mock feedback store backed by an in-memory list.

    In production this would write to PostgreSQL and/or Redis.
    The class interface is async so the real backend can be swapped in without
    changing callers.
    """

    def __init__(self) -> None:
        self._memory: list[dict[str, Any]] = []
        self._redis_url = settings.redis_url

    async def store(
        self,
        query_id: str,
        result_id: str,
        helpful: bool,
        comment: str | None,
    ) -> str:
        feedback_id = str(uuid.uuid4())
        record = {
            "feedback_id": feedback_id,
            "query_id": query_id,
            "result_id": result_id,
            "helpful": helpful,
            "comment": comment,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "storage": "memory",
        }
        self._memory.append(record)

        # Simulate Redis persistence: log the Redis URL so the intent is visible.
        logger.info(
            "feedback_stored",
            feedback_id=feedback_id,
            query_id=query_id,
            result_id=result_id,
            helpful=helpful,
            redis_url=self._redis_url,
        )
        return feedback_id

    async def get_feedback_for_result(self, result_id: str) -> list[dict[str, Any]]:
        return [r for r in self._memory if r["result_id"] == result_id]

    async def get_score(self, result_id: str) -> float:
        """Return net helpfulness score for a result in [-1, 1]."""
        entries = await self.get_feedback_for_result(result_id)
        if not entries:
            return 0.0
        helpful = sum(1 for e in entries if e["helpful"])
        return (2 * helpful / len(entries)) - 1

    def _serialize(self) -> str:
        return json.dumps(self._memory)
