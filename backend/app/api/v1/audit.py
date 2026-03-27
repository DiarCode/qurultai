from fastapi import APIRouter

from app.api.deps import SessionDep
from app.controllers.audit_controller import list_audit_logs
from app.schemas.audit import AuditLogRead

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/logs", response_model=list[AuditLogRead])
def get_audit_logs(session: SessionDep) -> list[AuditLogRead]:
    return list_audit_logs(session)
