from __future__ import annotations

from typing import Any

from pydantic import Field

from app.schemas.common import ORMModel


class RoomCreateRequest(ORMModel):
    query: str
    document_path: str | None = None


class RoomCreateResponse(ORMModel):
    room_id: str
    status: str
    thread_id: str | None = None


class RoomStatusResponse(ORMModel):
    room_id: str
    status: str
    mission_goals: list[str] = Field(default_factory=list)


class RoomReportResponse(ORMModel):
    room_id: str
    report_md: str | None
    report_html_path: str | None = None
    report_pdf_path: str | None = None


class RoomChatRequest(ORMModel):
    room_id: str
    query: str


class RoomChatResponse(ORMModel):
    answer: str


class AgentSourceRead(ORMModel):
    source_type: str | None
    ref_id: str | None
    snippet: str | None
    score: float | None


class AgentStepRead(ORMModel):
    id: str
    step_type: str
    content_json: dict[str, Any] | list[Any] | str
    created_at: str
    sources: list[AgentSourceRead] = Field(default_factory=list)


class AgentRunRead(ORMModel):
    id: str
    agent_id: str
    status: str
    bid_reason: str | None
    steps: list[AgentStepRead] = Field(default_factory=list)


class RoomTraceResponse(ORMModel):
    room_id: str
    status: str
    runs: list[AgentRunRead] = Field(default_factory=list)
