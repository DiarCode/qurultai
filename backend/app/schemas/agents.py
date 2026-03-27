from __future__ import annotations

from pydantic import Field

from app.schemas.common import AuditAwareResponse, ORMModel
from app.schemas.knowledge import KnowledgeDocumentRead
from app.schemas.tools import ToolRead


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


class AgentToolsResponse(ORMModel):
    agent_id: str
    tools: list[ToolRead] = Field(default_factory=list)


class AgentDocumentsResponse(ORMModel):
    agent_id: str
    documents: list[KnowledgeDocumentRead] = Field(default_factory=list)
