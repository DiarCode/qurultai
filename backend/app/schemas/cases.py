from __future__ import annotations

from datetime import datetime

from app.models.enums import AudienceMode, CaseRequestType, CaseStatus, InputMode
from app.schemas.common import AuditAwareResponse, ORMModel


class CaseCreate(ORMModel):
    title: str
    description: str
    request_type: CaseRequestType
    audience_mode: AudienceMode
    input_mode: InputMode
    status: CaseStatus = CaseStatus.SUBMITTED
    submitted_by_user_id: str | None = None
    source_document_id: str | None = None
    completed_at: datetime | None = None


class CaseRead(AuditAwareResponse):
    title: str
    description: str
    request_type: CaseRequestType
    audience_mode: AudienceMode
    input_mode: InputMode
    status: CaseStatus
    submitted_by_user_id: str | None
    source_document_id: str | None
    completed_at: datetime | None
