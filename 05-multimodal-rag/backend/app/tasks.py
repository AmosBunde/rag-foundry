import os
from typing import Any

from celery import Celery

from app.config import settings

broker_url = settings.celery_broker_url or settings.redis_url
result_backend = settings.celery_result_backend or settings.redis_url

# In eager/test mode, avoid needing a real Redis result backend.
_eager = os.environ.get("CELERY_TASK_ALWAYS_EAGER", "false").lower() == "true"
if _eager and result_backend.startswith("redis://"):
    result_backend = "cache+memory://"

celery_app = Celery(
    "multimodal_rag",
    broker=broker_url,
    backend=result_backend,
    include=["app.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_always_eager=_eager,
)


@celery_app.task(bind=True)
def process_media(self, modality: str, item_id: str | None, filename: str, content_type: str, file_bytes: bytes, metadata: dict[str, Any]) -> dict[str, Any]:
    """Celery task that processes image or audio ingestion asynchronously.

    When Celery is not configured, tasks run eagerly and call the ingestion service directly.
    """
    import asyncio

    from app.ingestion import IngestionService

    self.update_state(state="PROCESSING", meta={"modality": modality, "filename": filename})

    async def _run() -> dict[str, Any]:
        service = IngestionService()
        return await service.process_media_async(
            modality=modality,  # type: ignore[arg-type]
            item_id=item_id,
            filename=filename,
            content_type=content_type,
            file_bytes=file_bytes,
            metadata=metadata,
        )

    return asyncio.run(_run())
