from __future__ import annotations

from app.models.enums import AudienceMode, ReportStatus
from app.schemas.common import AuditAwareResponse, ORMModel


class ReportCreate(ORMModel):
    case_id: str
    orchestration_run_id: str | None = None
    audience_mode: AudienceMode
    title: str
    summary: str
    markdown_content: str
    html_path: str | None = None
    pdf_path: str | None = None
    status: ReportStatus = ReportStatus.DRAFT


class ReportRead(AuditAwareResponse):
    case_id: str
    orchestration_run_id: str | None
    audience_mode: AudienceMode
    title: str
    summary: str
    markdown_content: str
    html_path: str | None
    pdf_path: str | None
    status: ReportStatus
