from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.document_parser import auto_parse_document
from app.core.exceptions import NotFoundError
from app.core.utils import ensure_directory
from app.models.agent import Agent
from app.models.knowledge_document import AgentKnowledgeLink, KnowledgeDocument
from app.schemas.knowledge import KnowledgeDocumentRead
from app.services import qdrant_service, s3_service, text_preprocessing_service


def _knowledge_object_key(document_id: str, filename: str, agent_id: str | None) -> str:
    settings = get_settings()
    segment = agent_id or "unassigned"
    return f"{settings.S3_KNOWLEDGE_PREFIX}/{segment}/{document_id}/{filename}"


def _parse_text_from_temp_file(file_path: Path) -> tuple[str, str]:
    try:
        parsed, kind = auto_parse_document(str(file_path))
        return parsed, kind
    except Exception:
        return file_path.read_text(encoding="utf-8", errors="ignore"), "text"


def _document_status_fields(document: KnowledgeDocument) -> dict[str, Any]:
    metadata = dict(document.metadata_json or {})
    return {
        "metadata_json": metadata,
        "upload_status": str(metadata.get("upload_status") or "completed"),
        "index_status": str(metadata.get("index_status") or "completed"),
        "chunk_count": int(metadata.get("chunk_count") or 0),
        "parser_kind": str(metadata.get("parser_kind")) if metadata.get("parser_kind") else None,
    }


def build_document_read(
    document: KnowledgeDocument, *, agent_ids: list[str] | None = None
) -> KnowledgeDocumentRead:
    payload = KnowledgeDocumentRead.model_validate(document).model_dump()
    payload.update(_document_status_fields(document))
    payload["agent_ids"] = list(agent_ids or [])
    payload["download_url"] = f"/api/v1/files/{document.id}/download"
    return KnowledgeDocumentRead(**payload)


def upload_document(
    session: Session,
    *,
    source_filename: str,
    payload: bytes,
    mime_type: str,
    agent_id: str | None = None,
    title: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> tuple[KnowledgeDocument, int]:
    agent: Agent | None = None
    if agent_id:
        agent = session.get(Agent, agent_id)
        if agent is None:
            raise NotFoundError(f"Agent '{agent_id}' was not found.")

    filename = source_filename or "document.bin"

    settings = get_settings()
    initial_metadata = {
        "source": "upload",
        "upload_status": "uploaded",
        "index_status": "processing",
        **(metadata or {}),
    }

    doc = KnowledgeDocument(
        title=title or filename,
        source_filename=filename,
        mime_type=mime_type,
        size_bytes=len(payload),
        s3_bucket=settings.MINIO_BUCKET,
        s3_key="",
        text_preview=None,
        metadata_json=initial_metadata,
    )
    session.add(doc)
    session.flush()

    object_key = _knowledge_object_key(doc.id, filename, agent_id)
    s3_service.upload_bytes(object_key, payload, content_type=mime_type)

    uploads_dir = ensure_directory(settings.uploads_dir_path)
    safe_filename = filename.replace("\\", "_").replace("/", "_")
    temp_path = Path(uploads_dir) / f"kb_{doc.id}_{safe_filename}"
    temp_path.write_bytes(payload)
    extracted_text, parser_kind = _parse_text_from_temp_file(temp_path)
    try:
        temp_path.unlink(missing_ok=True)
    except Exception:
        pass

    chunks = text_preprocessing_service.split_into_chunks(extracted_text)
    try:
        chunks_ingested = qdrant_service.ingest_document_chunks(
            doc.id,
            agent_id,
            chunks,
            object_key,
            title=doc.title,
            mime_type=mime_type,
        )
        index_status = "completed"
    except Exception:
        chunks_ingested = 0
        index_status = "failed"

    doc.s3_key = object_key
    doc.text_preview = extracted_text[:500] if extracted_text else None
    doc.metadata_json = {
        **dict(doc.metadata_json or {}),
        "source": (metadata or {}).get("source", "upload"),
        "upload_status": "completed",
        "index_status": index_status,
        "chunk_count": len(chunks),
        "chunks_ingested": chunks_ingested,
        "parser_kind": parser_kind,
    }
    if agent is not None:
        session.add(AgentKnowledgeLink(agent_id=agent.id, document_id=doc.id))

    session.add(doc)
    session.commit()
    session.refresh(doc)
    return doc, chunks_ingested


def list_documents(session: Session, agent_id: str | None = None) -> list[KnowledgeDocument]:
    if not agent_id:
        return list(
            session.exec(select(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc()))
        )

    agent = session.get(Agent, agent_id)
    if agent is None:
        raise NotFoundError(f"Agent '{agent_id}' was not found.")
    links = list(
        session.exec(select(AgentKnowledgeLink).where(AgentKnowledgeLink.agent_id == agent_id))
    )
    if not links:
        return []
    return list(
        session.exec(
            select(KnowledgeDocument)
            .where(KnowledgeDocument.id.in_([link.document_id for link in links]))
            .order_by(KnowledgeDocument.created_at.desc())
        )
    )


def get_document(session: Session, document_id: str) -> KnowledgeDocument:
    doc = session.get(KnowledgeDocument, document_id)
    if doc is None:
        raise NotFoundError(f"Knowledge document '{document_id}' was not found.")
    return doc


def delete_document(session: Session, document_id: str) -> None:
    doc = get_document(session, document_id)
    links = list(
        session.exec(
            select(AgentKnowledgeLink).where(AgentKnowledgeLink.document_id == document_id)
        )
    )
    for link in links:
        session.delete(link)

    s3_service.delete_object(doc.s3_key)
    try:
        qdrant_service.delete_document_points(document_id)
    except Exception:
        pass

    session.delete(doc)
    session.commit()


def search_documents(
    session: Session,
    query: str,
    limit: int = 5,
    agent_id: str | None = None,
) -> list[dict[str, str | float | int | None]]:
    try:
        hits = qdrant_service.search(query=query, limit=limit, agent_id=agent_id)
        if hits:
            return hits
    except Exception:
        pass

    documents = list_documents(session, agent_id)
    query_tokens = {token.lower() for token in query.split() if token.strip()}
    ranked: list[dict[str, str | float | int | None]] = []
    for document in documents:
        preview = document.text_preview or ""
        haystack = f"{document.title} {preview}".lower()
        score = sum(1 for token in query_tokens if token in haystack)
        if score <= 0:
            continue
        ranked.append(
            {
                "document_id": document.id,
                "agent_id": agent_id,
                "title": document.title,
                "mime_type": document.mime_type,
                "text": preview,
                "s3_key": document.s3_key,
                "score": min(1.0, score / max(1, len(query_tokens))),
                "chunk_index": 1,
                "chunk_count": int((document.metadata_json or {}).get("chunk_count") or 1),
                "location": "Document preview",
            }
        )

    ranked.sort(key=lambda item: float(item["score"] or 0.0), reverse=True)
    return ranked[:limit]


def get_document_download(
    session: Session, document_id: str, expires_hours: int = 24
) -> tuple[str, str | None]:
    doc = get_document(session, document_id)
    s3_uri = s3_service.s3_uri(doc.s3_key)
    presigned = s3_service.make_presigned_get_url(doc.s3_key, expires_hours=expires_hours)
    return s3_uri, presigned
