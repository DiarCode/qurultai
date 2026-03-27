from __future__ import annotations

from sqlmodel import Session, select

from app.models.audit_log import AuditLog


def log_event(
    session: Session,
    *,
    entity_type: str,
    entity_id: str,
    action: str,
    actor_user_id: str | None = None,
    details_json: dict[str, object] | None = None,
) -> AuditLog:
    audit_log = AuditLog(
        actor_user_id=actor_user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        details_json=details_json or {},
    )
    session.add(audit_log)
    return audit_log


def list_audit_logs(session: Session) -> list[AuditLog]:
    statement = select(AuditLog).order_by(AuditLog.created_at.desc())
    return list(session.exec(statement))
