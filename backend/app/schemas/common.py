from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampedResponse(ORMModel):
    id: str
    created_at: datetime


class AuditAwareResponse(TimestampedResponse):
    updated_at: datetime


class AgentReference(ORMModel):
    id: str
    key: str
    name: str


class KnowledgeSourceReference(ORMModel):
    id: str
    key: str | None
    name: str
    source_type: str
    status: str


class SkillReference(ORMModel):
    id: str
    key: str
    name: str
    category: str
    is_active: bool


JsonDict = dict[str, Any]
