import os

import pytest

from app.tasks import celery_app, process_media


def test_celery_config() -> None:
    assert celery_app.main == "multimodal_rag"
    assert celery_app.conf.task_serializer == "json"


def test_process_media_task_image(mocker) -> None:
    mock_service = mocker.patch("app.ingestion.IngestionService")
    mock_service.return_value.process_media_async = mocker.AsyncMock(
        return_value={"id": "img-1", "status": "indexed", "caption": "A cat"}
    )

    result = process_media.apply(args=["image", "img-1", "cat.png", "image/png", b"fake", {}])
    assert result.successful()
    assert result.result["status"] == "indexed"
    assert result.result["caption"] == "A cat"
