from fastapi import APIRouter
from fastapi.responses import Response

from app.api.deps import SessionDep
from app.controllers import knowledge_controller
from app.schemas.knowledge import (
    KnowledgeDocumentDownloadResponse,
    KnowledgeDocumentListResponse,
    KnowledgeDocumentUploadRequest,
    KnowledgeDocumentUploadResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("/documents/upload", response_model=KnowledgeDocumentUploadResponse, status_code=201)
def upload_document(
    session: SessionDep,
    payload: KnowledgeDocumentUploadRequest,
) -> KnowledgeDocumentUploadResponse:
    return knowledge_controller.upload_document(session, payload=payload)


@router.get("/documents", response_model=KnowledgeDocumentListResponse)
def list_documents(
    session: SessionDep, agent_id: str | None = None
) -> KnowledgeDocumentListResponse:
    return knowledge_controller.list_documents(session, agent_id=agent_id)


@router.delete("/documents/{document_id}", status_code=204)
def delete_document(document_id: str, session: SessionDep) -> Response:
    knowledge_controller.delete_document(session, document_id)
    return Response(status_code=204)


@router.post("/search", response_model=KnowledgeSearchResponse)
def search_documents(
    payload: KnowledgeSearchRequest, session: SessionDep
) -> KnowledgeSearchResponse:
    return knowledge_controller.search_documents(session, payload)


@router.get("/documents/{document_id}/download", response_model=KnowledgeDocumentDownloadResponse)
def get_document_download(
    document_id: str,
    session: SessionDep,
    expires_hours: int = 24,
) -> KnowledgeDocumentDownloadResponse:
    return knowledge_controller.get_document_download(
        session, document_id, expires_hours=expires_hours
    )
