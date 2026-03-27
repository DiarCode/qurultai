from __future__ import annotations

from pydantic import Field

from app.schemas.common import AuditAwareResponse, ORMModel


class AgentCreate(ORMModel):
    key: str
    name: str
    role_description: str
    system_prompt: str
    status: str = "active"
    tool_ids: list[str] = Field(default_factory=list)


class AgentUpdate(ORMModel):
    name: str | None = None
    role_description: str | None = None
    system_prompt: str | None = None
    status: str | None = None
    tool_ids: list[str] | None = None


class AgentRead(AuditAwareResponse):
    key: str
    name: str
    role_description: str
    system_prompt: str
    status: str
    tool_ids: list[str] = Field(default_factory=list)
