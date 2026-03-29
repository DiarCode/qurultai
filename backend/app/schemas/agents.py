from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from app.schemas.common import AuditAwareResponse, ORMModel
from app.schemas.knowledge import KnowledgeDocumentRead
from app.schemas.skills import SkillRead
from app.schemas.tools import ToolRead

AgentStatus = Literal["active", "draft", "paused"]


class AgentCreate(ORMModel):
    key: str | None = None
    name: str
    role: str | None = None
    role_description: str | None = None
    description: str | None = None
    system_prompt: str
    goals: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    status: AgentStatus = "active"
    skill_ids: list[str] = Field(default_factory=list)
    tool_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def normalize_role(self) -> "AgentCreate":
        role_value = self.role or self.role_description
        if not role_value:
            raise ValueError("role is required")
        self.role = role_value
        self.role_description = role_value
        return self


class AgentUpdate(ORMModel):
    key: str | None = None
    name: str | None = None
    role: str | None = None
    role_description: str | None = None
    description: str | None = None
    system_prompt: str | None = None
    goals: list[str] | None = None
    constraints: list[str] | None = None
    status: AgentStatus | None = None
    skill_ids: list[str] | None = None
    tool_ids: list[str] | None = None

    @model_validator(mode="after")
    def normalize_role(self) -> "AgentUpdate":
        if self.role is None and self.role_description is None:
            return self
        role_value = self.role or self.role_description
        self.role = role_value
        self.role_description = role_value
        return self


class AgentRead(AuditAwareResponse):
    key: str
    name: str
    role: str
    description: str | None
    system_prompt: str
    goals: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    status: AgentStatus
    tool_ids: list[str] = Field(default_factory=list)
    skill_ids: list[str] = Field(default_factory=list)
    tools: list[ToolRead] = Field(default_factory=list)
    skills: list[SkillRead] = Field(default_factory=list)
    documents: list[KnowledgeDocumentRead] = Field(default_factory=list)


class AgentToolsResponse(ORMModel):
    agent_id: str
    tools: list[ToolRead] = Field(default_factory=list)


class AgentDocumentsResponse(ORMModel):
    agent_id: str
    documents: list[KnowledgeDocumentRead] = Field(default_factory=list)


class AgentSkillsResponse(ORMModel):
    agent_id: str
    skills: list[SkillRead] = Field(default_factory=list)
