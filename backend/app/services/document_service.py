from __future__ import annotations

import uuid

from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.exceptions import NotFoundError
from app.models.agent import Agent
from app.models.document import Document
from app.services import minio_service


def _generate_object_key(original_filename: str) -> str:
    unique = uuid.uuid4().hex[:12]
    safe_name = original_filename.replace(" ", "_")
    return f"documents/{unique}_{safe_name}"


def upload_document(
    session: Session,
    file_data: bytes,
    original_filename: str,
    content_type: str,
    description: str | None = None,
) -> Document:
    settings = get_settings()
    object_key = _generate_object_key(original_filename)

    minio_service.upload_file(
        data=file_data,
        object_key=object_key,
        content_type=content_type,
        bucket_name=settings.MINIO_BUCKET,
    )

    doc = Document(
        filename=original_filename,
        original_filename=original_filename,
        content_type=content_type,
        file_size=len(file_data),
        bucket_name=settings.MINIO_BUCKET,
        object_key=object_key,
        description=description,
    )
    session.add(doc)
    session.commit()
    session.refresh(doc)
    return doc


def upload_documents(
    session: Session,
    files: list[tuple[bytes, str, str]],
    description: str | None = None,
) -> list[Document]:
    docs = []
    for file_data, original_filename, content_type in files:
        doc = upload_document(session, file_data, original_filename, content_type, description)
        docs.append(doc)
    return docs


def get_document(session: Session, document_id: str) -> Document:
    doc = session.get(Document, document_id)
    if doc is None:
        raise NotFoundError(f"Document '{document_id}' was not found.")
    return doc


def list_documents(session: Session) -> list[Document]:
    return list(session.exec(select(Document).order_by(Document.created_at.desc())))


def download_document(session: Session, document_id: str) -> tuple[bytes, Document]:
    doc = get_document(session, document_id)
    data = minio_service.download_file(doc.object_key, doc.bucket_name)
    return data, doc


def delete_document(session: Session, document_id: str) -> None:
    doc = get_document(session, document_id)
    minio_service.delete_file(doc.object_key, doc.bucket_name)
    session.delete(doc)
    session.commit()


def delete_documents(session: Session, document_ids: list[str]) -> int:
    deleted = 0
    for doc_id in document_ids:
        try:
            delete_document(session, doc_id)
            deleted += 1
        except NotFoundError:
            pass
    return deleted


def attach_documents_to_agent(session: Session, agent_id: str, document_ids: list[str]) -> Agent:
    agent = session.get(Agent, agent_id)
    if agent is None:
        raise NotFoundError(f"Agent '{agent_id}' was not found.")

    existing_doc_ids = {doc.id for doc in agent.documents}

    for doc_id in document_ids:
        if doc_id in existing_doc_ids:
            continue
        doc = get_document(session, doc_id)
        agent.documents.append(doc)

    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent


def detach_documents_from_agent(session: Session, agent_id: str, document_ids: list[str]) -> Agent:
    agent = session.get(Agent, agent_id)
    if agent is None:
        raise NotFoundError(f"Agent '{agent_id}' was not found.")

    agent.documents = [doc for doc in agent.documents if doc.id not in document_ids]

    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent
