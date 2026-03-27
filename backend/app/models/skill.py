from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.core.utils import utc_now
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.agent import Agent


class AgentSkillLink(SQLModel, table=True):
    __tablename__ = "agent_skill_links"
    __table_args__ = (UniqueConstraint("agent_id", "skill_id", name="uq_agent_skill_link"),)

    agent_id: str = Field(foreign_key="agents.id", primary_key=True, max_length=36)
    skill_id: str = Field(foreign_key="skills.id", primary_key=True, max_length=36)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)


class Skill(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    __tablename__ = "skills"

    key: str = Field(index=True, unique=True, max_length=100)
    name: str = Field(max_length=255)
    description: str | None = Field(default=None)
    category: str = Field(max_length=100)
    config_json: dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    is_active: bool = Field(default=True)

    agents: list["Agent"] = Relationship(back_populates="skills", link_model=AgentSkillLink)
