from typing import Optional

from fastapi import APIRouter, File, Form, Response, UploadFile

from app.api.deps import SessionDep
from app.schemas.documents import (
    DocumentDeleteRequest,
    DocumentDeleteResponse,
    DocumentRead,
)
from app.services import document_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=list[DocumentRead], status_code=201)
async def upload_documents(
    session: SessionDep,
    files: list[UploadFile] = File(...),
    description: Optional[str] = Form(None),
) -> list[DocumentRead]:
    file_tuples = []
    for f in files:
        data = await f.read()
        file_tuples.append(
            (data, f.filename or "unknown", f.content_type or "application/octet-stream")
        )
    docs = document_service.upload_documents(session, file_tuples, description)
    return [DocumentRead.model_validate(doc) for doc in docs]


@router.get("", response_model=list[DocumentRead])
def list_documents(session: SessionDep) -> list[DocumentRead]:
    docs = document_service.list_documents(session)
    return [DocumentRead.model_validate(doc) for doc in docs]


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(document_id: str, session: SessionDep) -> DocumentRead:
    doc = document_service.get_document(session, document_id)
    return DocumentRead.model_validate(doc)


@router.get("/{document_id}/download")
def download_document(document_id: str, session: SessionDep) -> Response:
    data, doc = document_service.download_document(session, document_id)
    return Response(
        content=data,
        media_type=doc.content_type,
        headers={"Content-Disposition": f'attachment; filename="{doc.original_filename}"'},
    )


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: str, session: SessionDep) -> None:
    document_service.delete_document(session, document_id)


@router.post("/bulk-delete", response_model=DocumentDeleteResponse)
def bulk_delete_documents(
    payload: DocumentDeleteRequest, session: SessionDep
) -> DocumentDeleteResponse:
    count = document_service.delete_documents(session, payload.document_ids)
    return DocumentDeleteResponse(deleted_count=count)
