from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import Response

from app.api.deps import SessionDep
from app.services import council_service

router = APIRouter(prefix="/files", tags=["files"])


@router.get("/{document_id}/download")
def download_document(document_id: str, session: SessionDep) -> Response:
    payload, media_type, filename = council_service.load_document_bytes(session, document_id)
    return Response(
        content=payload,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
