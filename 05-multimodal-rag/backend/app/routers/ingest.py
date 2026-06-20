import json
from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.auth import User, get_current_user
from app.config import settings
from app.guardrails import guard_media, guard_query
from app.ingestion import IngestionService
from app.models import AudioIngestResponse, ImageIngestResponse, IngestResponse, TextIngestRequest
from app.tasks import process_media

router = APIRouter(prefix="/api/v1/ingest", tags=["ingest"])


def _get_service() -> IngestionService:
    return IngestionService()


@router.post("/text", response_model=IngestResponse)
async def ingest_text(
    request: TextIngestRequest,
    user: User = Depends(get_current_user),
    service: IngestionService = Depends(_get_service),
) -> IngestResponse:
    for doc in request.documents:
        guard_query(doc.text, max_length=settings.max_text_length)
    return await service.ingest_text(request.documents)


@router.post("/image", response_model=ImageIngestResponse)
async def ingest_image(
    file: Annotated[UploadFile, File()],
    image_id: Annotated[str | None, Form()] = None,
    metadata: Annotated[str, Form()] = "{}",
    user: User = Depends(get_current_user),
    service: IngestionService = Depends(_get_service),
) -> ImageIngestResponse:
    if file.content_type not in settings.supported_image_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported image type: {file.content_type}. Supported: {settings.supported_image_types}",
        )

    file_bytes = await file.read()
    guard_media(file.filename, file.content_type, len(file_bytes), settings.max_image_size_mb)

    try:
        meta = json.loads(metadata)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid metadata JSON") from exc

    return await service.ingest_image(image_id, file.filename or "image.bin", file.content_type, file_bytes, meta)


@router.post("/audio", response_model=AudioIngestResponse)
async def ingest_audio(
    file: Annotated[UploadFile, File()],
    audio_id: Annotated[str | None, Form()] = None,
    metadata: Annotated[str, Form()] = "{}",
    user: User = Depends(get_current_user),
    service: IngestionService = Depends(_get_service),
) -> AudioIngestResponse:
    if file.content_type not in settings.supported_audio_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported audio type: {file.content_type}. Supported: {settings.supported_audio_types}",
        )

    file_bytes = await file.read()
    guard_media(file.filename, file.content_type, len(file_bytes), settings.max_audio_size_mb)

    try:
        meta = json.loads(metadata)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid metadata JSON") from exc

    return await service.ingest_audio(audio_id, file.filename or "audio.bin", file.content_type, file_bytes, meta)


@router.post("/image/async")
async def ingest_image_async(
    file: Annotated[UploadFile, File()],
    image_id: Annotated[str | None, Form()] = None,
    metadata: Annotated[str, Form()] = "{}",
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    if file.content_type not in settings.supported_image_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported image type: {file.content_type}",
        )
    file_bytes = await file.read()
    guard_media(file.filename, file.content_type, len(file_bytes), settings.max_image_size_mb)
    meta = json.loads(metadata) if metadata else {}
    task = process_media.delay("image", image_id, file.filename or "image.bin", file.content_type, file_bytes, meta)
    return {"task_id": task.id, "status": "queued", "modality": "image"}


@router.post("/audio/async")
async def ingest_audio_async(
    file: Annotated[UploadFile, File()],
    audio_id: Annotated[str | None, Form()] = None,
    metadata: Annotated[str, Form()] = "{}",
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    if file.content_type not in settings.supported_audio_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported audio type: {file.content_type}",
        )
    file_bytes = await file.read()
    guard_media(file.filename, file.content_type, len(file_bytes), settings.max_audio_size_mb)
    meta = json.loads(metadata) if metadata else {}
    task = process_media.delay("audio", audio_id, file.filename or "audio.bin", file.content_type, file_bytes, meta)
    return {"task_id": task.id, "status": "queued", "modality": "audio"}
