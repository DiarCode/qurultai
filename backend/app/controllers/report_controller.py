from __future__ import annotations

from sqlmodel import Session

from app.schemas.reports import ReportCreate, ReportRead
from app.services import report_service


def create_report(session: Session, payload: ReportCreate) -> ReportRead:
    return ReportRead.model_validate(report_service.create_report(session, payload))


def list_reports(session: Session) -> list[ReportRead]:
    return [ReportRead.model_validate(report) for report in report_service.list_reports(session)]


def get_report(session: Session, report_id: str) -> ReportRead:
    return ReportRead.model_validate(report_service.get_report(session, report_id))
