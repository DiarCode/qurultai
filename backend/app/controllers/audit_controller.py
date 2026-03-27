from __future__ import annotations

from sqlmodel import Session

from app.schemas.audit import AuditLogRead
from app.services import audit_service


def list_audit_logs(session: Session) -> list[AuditLogRead]:
    return [AuditLogRead.model_validate(log) for log in audit_service.list_audit_logs(session)]
