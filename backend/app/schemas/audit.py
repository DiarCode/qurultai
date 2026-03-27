from __future__ import annotations

from datetime import datetime
from typing import Any

from app.schemas.common import ORMModel


class AuditLogRead(ORMModel):
    id: str
    actor_user_id: str | None
    entity_type: str
    entity_id: str
    action: str
    details_json: dict[str, Any]
    created_at: datetime
