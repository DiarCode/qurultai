from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from app.schemas.common import ORMModel

RunStatus = Literal["queued", "processing", "completed", "failed"]


class FileReferenceRead(ORMModel):
    id: str
    name: str
    mime_type: str | None = None
    size_bytes: int = 0
    linked_entity_type: str
    linked_entity_id: str
    created_at: datetime
    download_url: str | None = None
    text_preview: str | None = None
    upload_status: str = "completed"
    index_status: str = "completed"
    chunk_count: int = 0
    parser_kind: str | None = None


class RunParticipantRead(ORMModel):
    id: str
    key: str
    name: str
    role: str
    status: str


class CitationRead(ORMModel):
    id: str
    document_id: str | None = None
    title: str
    snippet: str | None = None
    score: float | None = None
    location: str | None = None
    download_url: str | None = None


class ToolCallRead(ORMModel):
    name: str
    status: str
    input: dict[str, Any] = Field(default_factory=dict)
    output_summary: str | None = None


class RunMessageRead(ORMModel):
    id: str
    run_id: str
    role: str
    source_agent_id: str | None = None
    source_agent_name: str | None = None
    stage: str | None = None
    status: str
    content: str
    citations: list[CitationRead] = Field(default_factory=list)
    tool_calls: list[ToolCallRead] = Field(default_factory=list)
    is_partial: bool = False
    created_at: datetime


class ReportVariantRead(ORMModel):
    format: Literal["markdown", "html", "pdf"]
    download_url: str
    available: bool = True


class RunReportRead(ORMModel):
    title: str
    summary: str
    body_markdown: str
    body_html: str
    source_agent_name: str | None = None
    generated_at: datetime | None = None
    variants: list[ReportVariantRead] = Field(default_factory=list)


class RunEventRead(ORMModel):
    id: str
    run_id: str
    sequence: int
    event_type: str
    created_at: datetime
    payload: dict[str, Any] = Field(default_factory=dict)


class RunCreateResponse(ORMModel):
    run_id: str
    status: RunStatus
    websocket_url: str


class RunRead(ORMModel):
    id: str
    prompt: str
    status: RunStatus
    created_at: datetime
    updated_at: datetime
    participants: list[RunParticipantRead] = Field(default_factory=list)
    attachments: list[FileReferenceRead] = Field(default_factory=list)
    messages: list[RunMessageRead] = Field(default_factory=list)
    final_report: RunReportRead | None = None
    events: list[RunEventRead] = Field(default_factory=list)


class RunListResponse(ORMModel):
    items: list[RunRead] = Field(default_factory=list)
