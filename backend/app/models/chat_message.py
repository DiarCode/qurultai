from __future__ import annotations

from typing import Any

from sqlalchemy import JSON
from sqlmodel import Field

from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class ChatMessage(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    __tablename__ = "chat_messages"

    session_id: str = Field(foreign_key="rooms.id", index=True, max_length=36)
    run_id: str | None = Field(default=None, foreign_key="chat_runs.id", index=True, max_length=36)
    role: str = Field(max_length=40, index=True)
    message_type: str = Field(default="message", max_length=60, index=True)
    source_agent_id: str | None = Field(default=None, max_length=36)
    source_agent_name: str | None = Field(default=None, max_length=255)
    content: str = Field(default="")
    html_content: str | None = Field(default=None)
    citations_json: list[dict[str, Any]] = Field(default_factory=list, sa_type=JSON)
    attachments_json: list[dict[str, Any]] = Field(default_factory=list, sa_type=JSON)
    actions_json: list[dict[str, Any]] = Field(default_factory=list, sa_type=JSON)
    metadata_json: dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    status: str = Field(default="completed", max_length=40, index=True)

