from __future__ import annotations

from sqlmodel import Session

from app.schemas.cases import CaseCreate, CaseRead
from app.services import case_service


def create_case(session: Session, payload: CaseCreate) -> CaseRead:
    return CaseRead.model_validate(case_service.create_case(session, payload))


def list_cases(session: Session) -> list[CaseRead]:
    return [CaseRead.model_validate(case_item) for case_item in case_service.list_cases(session)]


def get_case(session: Session, case_id: str) -> CaseRead:
    return CaseRead.model_validate(case_service.get_case(session, case_id))
