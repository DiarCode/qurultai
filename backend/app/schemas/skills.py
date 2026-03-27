from __future__ import annotations

from pydantic import Field

from app.schemas.common import AuditAwareResponse, ORMModel


class SkillCreate(ORMModel):
    key: str
    name: str
    description: str | None = None
    content_md: str = ""


class SkillUpdate(ORMModel):
    name: str | None = None
    description: str | None = None
    content_md: str | None = None


class SkillRead(AuditAwareResponse):
    key: str
    name: str
    description: str | None
    content_md: str
    file_path: str | None


class AgentSkillRequest(ORMModel):
    skill_ids: list[str] = Field(min_length=1)


class AgentSkillContentRead(ORMModel):
    skill_id: str
    key: str
    name: str
    content_md: str
