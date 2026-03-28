from __future__ import annotations

from typing import Any

from pydantic import Field

from app.schemas.common import AuditAwareResponse, ORMModel


class ToolCreate(ORMModel):
    name: str
    description: str | None = None
    input_schema_json: dict[str, Any] = Field(default_factory=dict)
    endpoint_url: str | None = None


class ToolUpdate(ORMModel):
    name: str | None = None
    description: str | None = None
    input_schema_json: dict[str, Any] | None = None
    endpoint_url: str | None = None


class ToolRead(AuditAwareResponse):
    name: str
    description: str | None
    input_schema_json: dict[str, Any] = Field(default_factory=dict)
    endpoint_url: str | None
