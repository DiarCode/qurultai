from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON
from sqlmodel import Field, Relationship

from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AgentStatus
from app.models.knowledge_source import AgentKnowledgeSourceLink
from app.models.skill import AgentSkillLink

if TYPE_CHECKING:
    from app.models.case_message import CaseMessage
    from app.models.knowledge_source import KnowledgeSource
    from app.models.skill import Skill
    from app.models.user import User


class Agent(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    __tablename__ = "agents"

    key: str = Field(index=True, unique=True, max_length=100)
    name: str = Field(max_length=255)
    role: str = Field(max_length=100)
    description: str | None = Field(default=None)
    system_prompt: str = Field()
    goals_json: list[str] = Field(default_factory=list, sa_type=JSON)
    constraints_json: list[str] = Field(default_factory=list, sa_type=JSON)
    output_template: str | None = Field(default=None)
    status: AgentStatus = Field(default=AgentStatus.DRAFT, max_length=50)
    owner_user_id: str | None = Field(default=None, foreign_key="users.id", index=True, max_length=36)

    owner: "User | None" = Relationship(back_populates="owned_agents")
    skills: list["Skill"] = Relationship(back_populates="agents", link_model=AgentSkillLink)
    knowledge_sources: list["KnowledgeSource"] = Relationship(
        back_populates="agents",
        link_model=AgentKnowledgeSourceLink,
    )
    messages: list["CaseMessage"] = Relationship(back_populates="agent")
