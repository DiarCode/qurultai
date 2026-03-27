from fastapi import APIRouter

from app.api.deps import SessionDep
from app.controllers import case_controller
from app.schemas.cases import CaseCreate, CaseRead

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("", response_model=CaseRead, status_code=201)
def create_case(payload: CaseCreate, session: SessionDep) -> CaseRead:
    return case_controller.create_case(session, payload)


@router.get("", response_model=list[CaseRead])
def list_cases(session: SessionDep) -> list[CaseRead]:
    return case_controller.list_cases(session)


@router.get("/{case_id}", response_model=CaseRead)
def get_case(case_id: str, session: SessionDep) -> CaseRead:
    return case_controller.get_case(session, case_id)
