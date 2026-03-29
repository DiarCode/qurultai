from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, UniqueConstraint
from sqlmodel import Field

from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class ChatRunEvent(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    __tablename__ = "chat_run_events"
    __table_args__ = (UniqueConstraint("run_id", "sequence", name="uq_chat_run_event_sequence"),)

    run_id: str = Field(foreign_key="chat_runs.id", index=True, max_length=36)
    sequence: int = Field(index=True, ge=1)
    event_type: str = Field(index=True, max_length=80)
    payload_json: dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
