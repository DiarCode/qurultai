from __future__ import annotations

from sqlmodel import Session, select

from app.core.exceptions import NotFoundError
from app.models.case import Case
from app.models.orchestration_run import OrchestrationRun
from app.models.report import Report
from app.schemas.reports import ReportCreate
from app.services import audit_service


def _validate_report_dependencies(session: Session, payload: ReportCreate) -> OrchestrationRun | None:
    if session.get(Case, payload.case_id) is None:
        raise NotFoundError(f"Case '{payload.case_id}' was not found.")
    if payload.orchestration_run_id is None:
        return None
    orchestration_run = session.get(OrchestrationRun, payload.orchestration_run_id)
    if orchestration_run is None:
        raise NotFoundError(f"Orchestration run '{payload.orchestration_run_id}' was not found.")
    if orchestration_run.case_id != payload.case_id:
        raise NotFoundError(
            f"Orchestration run '{payload.orchestration_run_id}' does not belong to case '{payload.case_id}'."
        )
    return orchestration_run


def create_report(session: Session, payload: ReportCreate) -> Report:
    orchestration_run = _validate_report_dependencies(session, payload)
    report = Report(**payload.model_dump())
    session.add(report)
    session.flush()
    if orchestration_run is not None:
        orchestration_run.final_report_id = report.id
        session.add(orchestration_run)
    audit_service.log_event(
        session,
        entity_type="report",
        entity_id=report.id,
        action="created",
        details_json={"case_id": payload.case_id, "title": payload.title},
    )
    session.commit()
    session.refresh(report)
    return report


def list_reports(session: Session) -> list[Report]:
    statement = select(Report).order_by(Report.created_at.desc())
    return list(session.exec(statement))


def get_report(session: Session, report_id: str) -> Report:
    report = session.get(Report, report_id)
    if report is None:
        raise NotFoundError(f"Report '{report_id}' was not found.")
    return report
