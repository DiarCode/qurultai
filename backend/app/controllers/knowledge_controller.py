from __future__ import annotations

from sqlmodel import Session

from app.schemas.common import AgentReference
from app.schemas.knowledge import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentRead,
    KnowledgeSourceCreate,
    KnowledgeSourceRead,
)
from app.services import knowledge_service


def _to_knowledge_source_read(source: object) -> KnowledgeSourceRead:
    response = KnowledgeSourceRead.model_validate(source)
    if hasattr(source, "agents"):
        response.linked_agents = [AgentReference.model_validate(agent) for agent in source.agents]
    return response


def create_knowledge_source(session: Session, payload: KnowledgeSourceCreate) -> KnowledgeSourceRead:
    source = knowledge_service.create_knowledge_source(session, payload)
    return _to_knowledge_source_read(source)


def list_knowledge_sources(session: Session) -> list[KnowledgeSourceRead]:
    return [_to_knowledge_source_read(source) for source in knowledge_service.list_knowledge_sources(session)]


def get_knowledge_source(session: Session, knowledge_source_id: str) -> KnowledgeSourceRead:
    return _to_knowledge_source_read(
        knowledge_service.get_knowledge_source(session, knowledge_source_id)
    )


def create_knowledge_document(
    session: Session,
    payload: KnowledgeDocumentCreate,
) -> KnowledgeDocumentRead:
    return KnowledgeDocumentRead.model_validate(
        knowledge_service.create_knowledge_document(session, payload)
    )


def list_knowledge_documents(session: Session) -> list[KnowledgeDocumentRead]:
    return [
        KnowledgeDocumentRead.model_validate(document)
        for document in knowledge_service.list_knowledge_documents(session)
    ]


def get_knowledge_document(session: Session, document_id: str) -> KnowledgeDocumentRead:
    return KnowledgeDocumentRead.model_validate(
        knowledge_service.get_knowledge_document(session, document_id)
    )
