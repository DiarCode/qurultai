from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON
from sqlmodel import Field, Relationship

from app.core.utils import utc_now
from app.models.common import UUIDPrimaryKeyMixin
from app.models.enums import AuthorType, MessageType

if TYPE_CHECKING:
    from app.models.agent import Agent
    from app.models.case import Case


class CaseMessage(UUIDPrimaryKeyMixin, table=True):
    __tablename__ = "case_messages"

    case_id: str = Field(foreign_key="cases.id", index=True, max_length=36)
    parent_message_id: str | None = Field(default=None, foreign_key="case_messages.id", max_length=36)
    agent_id: str | None = Field(default=None, foreign_key="agents.id", index=True, max_length=36)
    author_type: AuthorType = Field(max_length=50)
    message_type: MessageType = Field(max_length=50)
    content_markdown: str = Field()
    citations_json: list[dict[str, Any]] = Field(default_factory=list, sa_type=JSON)
    pillar_scores_json: dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    tool_calls_json: list[dict[str, Any]] = Field(default_factory=list, sa_type=JSON)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)

    case: "Case" = Relationship(back_populates="messages")
    agent: "Agent | None" = Relationship(back_populates="messages")
