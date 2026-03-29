from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON
from sqlmodel import Field

from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class ChatRun(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    __tablename__ = "chat_runs"

    session_id: str = Field(foreign_key="rooms.id", index=True, max_length=36)
    input_message_id: str = Field(foreign_key="chat_messages.id", index=True, max_length=36)
    output_message_id: str | None = Field(default=None, max_length=36)
    mode: str = Field(default="direct_answer", max_length=60, index=True)
    status: str = Field(default="queued", max_length=40, index=True)
    selected_agents_json: list[dict[str, Any]] = Field(default_factory=list, sa_type=JSON)
    summary_json: dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    final_report_title: str | None = Field(default=None, max_length=255)
    final_report_md: str | None = Field(default=None)
    final_report_html: str | None = Field(default=None)
    started_at: datetime | None = Field(default=None, nullable=True)
    finished_at: datetime | None = Field(default=None, nullable=True)

