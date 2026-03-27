from __future__ import annotations

from sqlmodel import Session

from app.schemas.knowledge import (
    KnowledgeDocumentDownloadResponse,
    KnowledgeDocumentListResponse,
    KnowledgeDocumentRead,
    KnowledgeSearchHit,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    KnowledgeDocumentUploadRequest,
    KnowledgeDocumentUploadResponse,
)
from app.services import knowledge_service


def _to_read(doc) -> KnowledgeDocumentRead:
    data = KnowledgeDocumentRead.model_validate(doc).model_dump()
    data["agent_ids"] = list(getattr(doc, "agent_ids", []))
    return KnowledgeDocumentRead(**data)


def upload_document(
    session: Session,
    *,
    payload: KnowledgeDocumentUploadRequest,
) -> KnowledgeDocumentUploadResponse:
    raw_payload = bytes(payload.content_base64) if payload.content_base64 is not None else b""
    if not raw_payload and payload.plain_text is not None:
        raw_payload = payload.plain_text.encode("utf-8")

    doc, chunks_ingested = knowledge_service.upload_document(
        session,
        source_filename=payload.source_filename,
        payload=raw_payload,
        mime_type=payload.mime_type,
        agent_id=payload.agent_id,
        title=payload.title,
    )
    return KnowledgeDocumentUploadResponse(document=_to_read(doc), chunks_ingested=chunks_ingested)


def list_documents(session: Session, agent_id: str | None = None) -> KnowledgeDocumentListResponse:
    docs = knowledge_service.list_documents(session, agent_id=agent_id)
    return KnowledgeDocumentListResponse(items=[_to_read(doc) for doc in docs])


def delete_document(session: Session, document_id: str) -> None:
    knowledge_service.delete_document(session, document_id)


def search_documents(payload: KnowledgeSearchRequest) -> KnowledgeSearchResponse:
    hits = knowledge_service.search_documents(
        query=payload.query,
        limit=payload.limit,
        agent_id=payload.agent_id,
    )
    return KnowledgeSearchResponse(items=[KnowledgeSearchHit.model_validate(hit) for hit in hits])


def get_document_download(
    session: Session,
    document_id: str,
    expires_hours: int = 24,
) -> KnowledgeDocumentDownloadResponse:
    s3_uri, presigned = knowledge_service.get_document_download(
        session,
        document_id,
        expires_hours=expires_hours,
    )
    return KnowledgeDocumentDownloadResponse(document_id=document_id, s3_uri=s3_uri, presigned_url=presigned)
