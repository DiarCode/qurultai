from __future__ import annotations

from sqlmodel import Session, select

from app.core.exceptions import NotFoundError
from app.models.case import Case
from app.models.knowledge_document import KnowledgeDocument
from app.models.user import User
from app.schemas.cases import CaseCreate
from app.services import audit_service


def _validate_related_entities(
    session: Session,
    submitted_by_user_id: str | None,
    source_document_id: str | None,
) -> None:
    if submitted_by_user_id and session.get(User, submitted_by_user_id) is None:
        raise NotFoundError(f"User '{submitted_by_user_id}' was not found.")
    if source_document_id and session.get(KnowledgeDocument, source_document_id) is None:
        raise NotFoundError(f"Knowledge document '{source_document_id}' was not found.")


def create_case(session: Session, payload: CaseCreate) -> Case:
    _validate_related_entities(session, payload.submitted_by_user_id, payload.source_document_id)
    case = Case(**payload.model_dump())
    session.add(case)
    audit_service.log_event(
        session,
        entity_type="case",
        entity_id=case.id,
        action="created",
        actor_user_id=payload.submitted_by_user_id,
        details_json={"title": payload.title},
    )
    session.commit()
    session.refresh(case)
    return case


def list_cases(session: Session) -> list[Case]:
    statement = select(Case).order_by(Case.created_at.desc())
    return list(session.exec(statement))


def get_case(session: Session, case_id: str) -> Case:
    case = session.get(Case, case_id)
    if case is None:
        raise NotFoundError(f"Case '{case_id}' was not found.")
    return case
