from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON
from sqlmodel import Field, Relationship

from app.core.utils import utc_now
from app.models.common import UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


class AuditLog(UUIDPrimaryKeyMixin, table=True):
    __tablename__ = "audit_logs"

    actor_user_id: str | None = Field(default=None, foreign_key="users.id", index=True, max_length=36)
    entity_type: str = Field(index=True, max_length=100)
    entity_id: str = Field(index=True, max_length=36)
    action: str = Field(index=True, max_length=100)
    details_json: dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)

    actor: "User | None" = Relationship(back_populates="audit_logs")
