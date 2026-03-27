from __future__ import annotations

from typing import Any

from pydantic import Field

from app.schemas.common import AuditAwareResponse, ORMModel


class ToolCreate(ORMModel):
    name: str
    description: str | None = None
    tool_type: str = "custom"
    input_schema_json: dict[str, Any] = Field(default_factory=dict)
    output_schema_json: dict[str, Any] = Field(default_factory=dict)
    configuration_json: dict[str, Any] = Field(default_factory=dict)
    endpoint_url: str | None = None


class ToolUpdate(ORMModel):
    name: str | None = None
    description: str | None = None
    tool_type: str | None = None
    input_schema_json: dict[str, Any] | None = None
    output_schema_json: dict[str, Any] | None = None
    configuration_json: dict[str, Any] | None = None
    endpoint_url: str | None = None


class ToolRead(AuditAwareResponse):
    name: str
    description: str | None
    tool_type: str
    input_schema_json: dict[str, Any]
    output_schema_json: dict[str, Any]
    configuration_json: dict[str, Any]
    endpoint_url: str | None


class AgentToolRequest(ORMModel):
    tool_ids: list[str] = Field(min_length=1)
    config_overrides: dict[str, dict[str, Any]] | None = None


class AgentToolRead(ORMModel):
    tool_id: str
    name: str
    tool_type: str
    description: str | None
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    configuration: dict[str, Any]
    config_override: dict[str, Any]


class ToolExecuteRequest(ORMModel):
    tool_name: str
    params: dict[str, Any] = Field(default_factory=dict)


class ToolExecuteResponse(ORMModel):
    tool_name: str
    result: dict[str, Any]


class BuiltinToolDefinition(ORMModel):
    name: str
    description: str
    tool_type: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
