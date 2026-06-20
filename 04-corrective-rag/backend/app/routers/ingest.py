from fastapi import APIRouter, Depends, HTTPException

from app.auth import User, get_current_user
from app.guardrails import guard_query, validate_metadata
from app.ingestion import IngestionService
from app.models import IngestRequest, IngestResponse

router = APIRouter(prefix="/api/v1/ingest", tags=["ingest"])


@router.post("", response_model=IngestResponse)
async def ingest_documents(
    request: IngestRequest,
    user: User = Depends(get_current_user),
    service: IngestionService = Depends(IngestionService),
) -> IngestResponse:
    # Guardrail against overly long individual documents and suspicious metadata.
    for doc in request.documents:
        guard_query(doc.text, max_length=100_000)
        meta_result = validate_metadata(doc.metadata)
        if not meta_result.allowed:
            raise HTTPException(  # noqa: F821
                status_code=400,
                detail={"error": "Metadata guardrail violation", "reason": meta_result.reason},
            )
    return await service.ingest(request.documents)
