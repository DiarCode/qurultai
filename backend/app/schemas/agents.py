from __future__ import annotations

from pydantic import Field

from app.models.enums import AgentStatus
from app.schemas.common import AuditAwareResponse, KnowledgeSourceReference, ORMModel, SkillReference


class AgentCreate(ORMModel):
    key: str
    name: str
    role: str
    description: str | None = None
    system_prompt: str
    goals_json: list[str] = Field(default_factory=list)
    constraints_json: list[str] = Field(default_factory=list)
    output_template: str | None = None
    status: AgentStatus = AgentStatus.DRAFT
    owner_user_id: str | None = None
    skill_ids: list[str] = Field(default_factory=list)
    knowledge_source_ids: list[str] = Field(default_factory=list)


class AgentUpdate(ORMModel):
    name: str | None = None
    role: str | None = None
    description: str | None = None
    system_prompt: str | None = None
    goals_json: list[str] | None = None
    constraints_json: list[str] | None = None
    output_template: str | None = None
    status: AgentStatus | None = None
    owner_user_id: str | None = None
    skill_ids: list[str] | None = None
    knowledge_source_ids: list[str] | None = None


class AgentRead(AuditAwareResponse):
    key: str
    name: str
    role: str
    description: str | None
    system_prompt: str
    goals_json: list[str]
    constraints_json: list[str]
    output_template: str | None
    status: AgentStatus
    owner_user_id: str | None
    skills: list[SkillReference] = Field(default_factory=list)
    knowledge_sources: list[KnowledgeSourceReference] = Field(default_factory=list)
