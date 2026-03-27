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


JsonDict = dict[str, Any]
