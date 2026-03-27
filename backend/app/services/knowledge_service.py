from __future__ import annotations

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.core.exceptions import ConflictError, NotFoundError
from app.models.agent import Agent
from app.models.knowledge_document import KnowledgeDocument
from app.models.knowledge_source import KnowledgeSource
from app.models.user import User
from app.schemas.knowledge import KnowledgeDocumentCreate, KnowledgeSourceCreate
from app.services import audit_service


def _knowledge_source_query():
    return select(KnowledgeSource).options(
        selectinload(KnowledgeSource.agents),
        selectinload(KnowledgeSource.documents),
    )


def _validate_user(session: Session, user_id: str | None) -> None:
    if user_id and session.get(User, user_id) is None:
        raise NotFoundError(f"User '{user_id}' was not found.")


def _get_agents(session: Session, agent_ids: list[str]) -> list[Agent]:
    if not agent_ids:
        return []
    agents = list(session.exec(select(Agent).where(Agent.id.in_(agent_ids))))
    if len(agents) != len(set(agent_ids)):
        raise NotFoundError("One or more agent IDs were not found.")
    return agents


def create_knowledge_source(session: Session, payload: KnowledgeSourceCreate) -> KnowledgeSource:
    if payload.key:
        existing = session.exec(select(KnowledgeSource).where(KnowledgeSource.key == payload.key)).first()
        if existing is not None:
            raise ConflictError(f"Knowledge source key '{payload.key}' already exists.")
    _validate_user(session, payload.created_by_user_id)
    knowledge_source = KnowledgeSource(
        key=payload.key,
        name=payload.name,
        source_type=payload.source_type,
        description=payload.description,
        status=payload.status,
        metadata_json=payload.metadata_json,
        created_by_user_id=payload.created_by_user_id,
    )
    knowledge_source.agents = _get_agents(session, payload.agent_ids)
    session.add(knowledge_source)
    audit_service.log_event(
        session,
        entity_type="knowledge_source",
        entity_id=knowledge_source.id,
        action="created",
        actor_user_id=payload.created_by_user_id,
        details_json={"name": payload.name},
    )
    session.commit()
    session.refresh(knowledge_source)
    return get_knowledge_source(session, knowledge_source.id)


def list_knowledge_sources(session: Session) -> list[KnowledgeSource]:
    return list(session.exec(_knowledge_source_query().order_by(KnowledgeSource.created_at.desc())))


def get_knowledge_source(session: Session, knowledge_source_id: str) -> KnowledgeSource:
    knowledge_source = session.exec(
        _knowledge_source_query().where(KnowledgeSource.id == knowledge_source_id)
    ).first()
    if knowledge_source is None:
        raise NotFoundError(f"Knowledge source '{knowledge_source_id}' was not found.")
    return knowledge_source


def create_knowledge_document(
    session: Session,
    payload: KnowledgeDocumentCreate,
) -> KnowledgeDocument:
    knowledge_source = session.get(KnowledgeSource, payload.knowledge_source_id)
    if knowledge_source is None:
        raise NotFoundError(f"Knowledge source '{payload.knowledge_source_id}' was not found.")
    _validate_user(session, payload.uploaded_by_user_id)

    document = KnowledgeDocument(**payload.model_dump())
    session.add(document)
    audit_service.log_event(
        session,
        entity_type="knowledge_document",
        entity_id=document.id,
        action="created",
        actor_user_id=payload.uploaded_by_user_id,
        details_json={"knowledge_source_id": knowledge_source.id, "title": payload.title},
    )
    session.commit()
    session.refresh(document)
    return get_knowledge_document(session, document.id)


def list_knowledge_documents(session: Session) -> list[KnowledgeDocument]:
    statement = select(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc())
    return list(session.exec(statement))


def get_knowledge_document(session: Session, document_id: str) -> KnowledgeDocument:
    document = session.get(KnowledgeDocument, document_id)
    if document is None:
        raise NotFoundError(f"Knowledge document '{document_id}' was not found.")
    return document
