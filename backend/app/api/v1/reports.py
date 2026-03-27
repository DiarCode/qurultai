from fastapi import APIRouter

from app.api.deps import SessionDep
from app.controllers import report_controller
from app.schemas.reports import ReportCreate, ReportRead

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportRead, status_code=201)
def create_report(payload: ReportCreate, session: SessionDep) -> ReportRead:
    return report_controller.create_report(session, payload)


@router.get("", response_model=list[ReportRead])
def list_reports(session: SessionDep) -> list[ReportRead]:
    return report_controller.list_reports(session)


@router.get("/{report_id}", response_model=ReportRead)
def get_report(report_id: str, session: SessionDep) -> ReportRead:
    return report_controller.get_report(session, report_id)
