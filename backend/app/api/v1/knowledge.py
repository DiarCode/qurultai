from fastapi import APIRouter

from app.api.deps import SessionDep
from app.controllers import knowledge_controller
from app.schemas.knowledge import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentRead,
    KnowledgeSourceCreate,
    KnowledgeSourceRead,
)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("/sources", response_model=KnowledgeSourceRead, status_code=201)
def create_knowledge_source(
    payload: KnowledgeSourceCreate,
    session: SessionDep,
) -> KnowledgeSourceRead:
    return knowledge_controller.create_knowledge_source(session, payload)


@router.get("/sources", response_model=list[KnowledgeSourceRead])
def list_knowledge_sources(session: SessionDep) -> list[KnowledgeSourceRead]:
    return knowledge_controller.list_knowledge_sources(session)


@router.get("/sources/{knowledge_source_id}", response_model=KnowledgeSourceRead)
def get_knowledge_source(knowledge_source_id: str, session: SessionDep) -> KnowledgeSourceRead:
    return knowledge_controller.get_knowledge_source(session, knowledge_source_id)


@router.post("/documents", response_model=KnowledgeDocumentRead, status_code=201)
def create_knowledge_document(
    payload: KnowledgeDocumentCreate,
    session: SessionDep,
) -> KnowledgeDocumentRead:
    return knowledge_controller.create_knowledge_document(session, payload)


@router.get("/documents", response_model=list[KnowledgeDocumentRead])
def list_knowledge_documents(session: SessionDep) -> list[KnowledgeDocumentRead]:
    return knowledge_controller.list_knowledge_documents(session)


@router.get("/documents/{document_id}", response_model=KnowledgeDocumentRead)
def get_knowledge_document(document_id: str, session: SessionDep) -> KnowledgeDocumentRead:
    return knowledge_controller.get_knowledge_document(session, document_id)
