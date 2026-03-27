from __future__ import annotations

from pathlib import Path

from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.document_parser import auto_parse_document
from app.core.exceptions import NotFoundError
from app.core.utils import ensure_directory
from app.models.agent import Agent
from app.models.knowledge_document import AgentKnowledgeLink, KnowledgeDocument
from app.services import qdrant_service, s3_service, text_preprocessing_service


def _knowledge_object_key(document_id: str, filename: str, agent_id: str | None) -> str:
    settings = get_settings()
    segment = agent_id or "unassigned"
    return f"{settings.S3_KNOWLEDGE_PREFIX}/{segment}/{document_id}/{filename}"


def _parse_text_from_temp_file(file_path: Path) -> str:
    try:
        parsed, _kind = auto_parse_document(str(file_path))
        return parsed
    except Exception:
        return file_path.read_text(encoding="utf-8", errors="ignore")


def upload_document(
    session: Session,
    *,
    source_filename: str,
    payload: bytes,
    mime_type: str,
    agent_id: str | None = None,
    title: str | None = None,
) -> tuple[KnowledgeDocument, int]:
    agent: Agent | None = None
    if agent_id:
        agent = session.get(Agent, agent_id)
        if agent is None:
            raise NotFoundError(f"Agent '{agent_id}' was not found.")

    filename = source_filename or "document.bin"

    settings = get_settings()
    doc = KnowledgeDocument(
        title=title or filename,
        source_filename=filename,
        mime_type=mime_type,
        size_bytes=len(payload),
        s3_bucket=settings.MINIO_BUCKET,
        s3_key="",
        text_preview=None,
        metadata_json={"source": "upload"},
    )
    session.add(doc)
    session.flush()

    object_key = _knowledge_object_key(doc.id, filename, agent_id)
    s3_service.upload_bytes(object_key, payload, content_type=mime_type)

    uploads_dir = ensure_directory(settings.uploads_dir_path)
    safe_filename = filename.replace("\\", "_").replace("/", "_")
    temp_path = Path(uploads_dir) / f"kb_{doc.id}_{safe_filename}"
    temp_path.write_bytes(payload)
    extracted_text = _parse_text_from_temp_file(temp_path)
    try:
        temp_path.unlink(missing_ok=True)
    except Exception:
        pass

    chunks = text_preprocessing_service.split_into_chunks(extracted_text)
    chunks_ingested = qdrant_service.ingest_document_chunks(doc.id, agent_id, chunks, object_key)

    doc.s3_key = object_key
    doc.text_preview = extracted_text[:500] if extracted_text else None
    if agent is not None:
        session.add(AgentKnowledgeLink(agent_id=agent.id, document_id=doc.id))

    session.add(doc)
    session.commit()
    session.refresh(doc)
    setattr(doc, "agent_ids", [agent.id] if agent is not None else [])
    return doc, chunks_ingested


def _attach_agent_ids(session: Session, docs: list[KnowledgeDocument]) -> list[KnowledgeDocument]:
    if not docs:
        return docs

    doc_ids = [doc.id for doc in docs]
    links = list(session.exec(select(AgentKnowledgeLink).where(AgentKnowledgeLink.document_id.in_(doc_ids))))
    mapping: dict[str, list[str]] = {}
    for link in links:
        mapping.setdefault(link.document_id, []).append(link.agent_id)

    for doc in docs:
        setattr(doc, "agent_ids", mapping.get(doc.id, []))

    return docs


def list_documents(session: Session, agent_id: str | None = None) -> list[KnowledgeDocument]:
    if not agent_id:
        docs = list(session.exec(select(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc())))
        return _attach_agent_ids(session, docs)

    agent = session.get(Agent, agent_id)
    if agent is None:
        raise NotFoundError(f"Agent '{agent_id}' was not found.")
    links = list(session.exec(select(AgentKnowledgeLink).where(AgentKnowledgeLink.agent_id == agent_id)))
    if not links:
        return []
    docs = list(
        session.exec(
            select(KnowledgeDocument)
            .where(KnowledgeDocument.id.in_([link.document_id for link in links]))
            .order_by(KnowledgeDocument.created_at.desc())
        )
    )
    return _attach_agent_ids(session, docs)


def get_document(session: Session, document_id: str) -> KnowledgeDocument:
    doc = session.get(KnowledgeDocument, document_id)
    if doc is None:
        raise NotFoundError(f"Knowledge document '{document_id}' was not found.")
    links = list(session.exec(select(AgentKnowledgeLink).where(AgentKnowledgeLink.document_id == document_id)))
    setattr(doc, "agent_ids", [link.agent_id for link in links])
    return doc


def delete_document(session: Session, document_id: str) -> None:
    doc = get_document(session, document_id)
    links = list(session.exec(select(AgentKnowledgeLink).where(AgentKnowledgeLink.document_id == document_id)))
    for link in links:
        session.delete(link)

    s3_service.delete_object(doc.s3_key)
    try:
        qdrant_service.delete_document_points(document_id)
    except Exception:
        pass

    session.delete(doc)
    session.commit()


def search_documents(query: str, limit: int = 5, agent_id: str | None = None) -> list[dict[str, str | float | None]]:
    return qdrant_service.search(query=query, limit=limit, agent_id=agent_id)


def get_document_download(session: Session, document_id: str, expires_hours: int = 24) -> tuple[str, str | None]:
    doc = get_document(session, document_id)
    s3_uri = s3_service.s3_uri(doc.s3_key)
    presigned = s3_service.make_presigned_get_url(doc.s3_key, expires_hours=expires_hours)
    return s3_uri, presigned
