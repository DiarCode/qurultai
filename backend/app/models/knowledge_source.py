from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.core.utils import utc_now
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import KnowledgeSourceStatus, KnowledgeSourceType

if TYPE_CHECKING:
    from app.models.agent import Agent
    from app.models.knowledge_document import KnowledgeDocument
    from app.models.user import User


class AgentKnowledgeSourceLink(SQLModel, table=True):
    __tablename__ = "agent_knowledge_source_links"
    __table_args__ = (
        UniqueConstraint(
            "agent_id",
            "knowledge_source_id",
            name="uq_agent_knowledge_source_link",
        ),
    )

    agent_id: str = Field(foreign_key="agents.id", primary_key=True, max_length=36)
    knowledge_source_id: str = Field(
        foreign_key="knowledge_sources.id",
        primary_key=True,
        max_length=36,
    )
    created_at: datetime = Field(default_factory=utc_now, nullable=False)


class KnowledgeSource(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    __tablename__ = "knowledge_sources"

    key: str | None = Field(default=None, index=True, unique=True, max_length=100)
    name: str = Field(max_length=255)
    source_type: KnowledgeSourceType = Field(max_length=50)
    description: str | None = Field(default=None)
    status: KnowledgeSourceStatus = Field(default=KnowledgeSourceStatus.DRAFT, max_length=50)
    metadata_json: dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    created_by_user_id: str | None = Field(default=None, foreign_key="users.id", index=True, max_length=36)

    created_by: "User | None" = Relationship(back_populates="created_knowledge_sources")
    documents: list["KnowledgeDocument"] = Relationship(back_populates="knowledge_source")
    agents: list["Agent"] = Relationship(
        back_populates="knowledge_sources",
        link_model=AgentKnowledgeSourceLink,
    )
