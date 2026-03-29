from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.core.utils import utc_now
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.agent import Agent


class AgentSkillLink(SQLModel, table=True):
    __tablename__ = "agent_skills"
    __table_args__ = (UniqueConstraint("agent_id", "skill_id", name="uq_agent_skill"),)

    agent_id: str = Field(foreign_key="agents.id", primary_key=True, max_length=36)
    skill_id: str = Field(foreign_key="skills.id", primary_key=True, max_length=36)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)


class Skill(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    __tablename__ = "skills"

    key: str = Field(index=True, unique=True, max_length=100)
    name: str = Field(max_length=255)
    description: str | None = Field(default=None)
    content_md: str = Field(default="")
    file_path: str | None = Field(default=None, max_length=1024)

    agents: list["Agent"] = Relationship(back_populates="skills", link_model=AgentSkillLink)
