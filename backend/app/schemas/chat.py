from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from app.schemas.common import ORMModel

ChatRunMode = Literal["direct_answer", "rag_answer", "specialist_assist", "council"]
ChatModePreference = Literal["auto", "direct_answer", "rag_answer", "specialist_assist", "council"]
ChatRunStatus = Literal["queued", "processing", "completed", "failed"]


class CitationRead(ORMModel):
    id: str
    document_id: str | None = None
    title: str
    snippet: str | None = None
    score: float | None = None
    location: str | None = None
    download_url: str | None = None


class MessageAttachmentRead(ORMModel):
    id: str
    name: str
    mime_type: str | None = None
    size_bytes: int = 0
    download_url: str | None = None
    created_at: datetime | None = None


class MessageActionRead(ORMModel):
    id: str
    kind: str
    label: str
    icon: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class ChatMessageRead(ORMModel):
    id: str
    session_id: str
    run_id: str | None = None
    role: str
    type: str
    source_agent_id: str | None = None
    source_agent_name: str | None = None
    content: str
    html_content: str | None = None
    citations: list[CitationRead] = Field(default_factory=list)
    attachments: list[MessageAttachmentRead] = Field(default_factory=list)
    actions: list[MessageActionRead] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    status: str
    created_at: datetime


class ChatSessionSummaryRead(ORMModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    status: str
    last_message_preview: str | None = None


class UploadedDocumentRead(ORMModel):
    id: str
    session_id: str
    name: str
    mime_type: str | None = None
    size_bytes: int = 0
    storage_path: str | None = None
    download_url: str | None = None
    linked_run_id: str | None = None
    created_at: datetime


class ChatParticipantRead(ORMModel):
    id: str
    key: str
    name: str
    role: str
    status: str
    reason: str | None = None


class ChatRunEventRead(ORMModel):
    id: str
    run_id: str
    sequence: int
    event_type: str
    created_at: datetime
    payload: dict[str, Any] = Field(default_factory=dict)


class ChatRunRead(ORMModel):
    id: str
    session_id: str
    input_message_id: str
    output_message_id: str | None = None
    mode: ChatRunMode
    selected_agents: list[ChatParticipantRead] = Field(default_factory=list)
    status: ChatRunStatus
    started_at: datetime | None = None
    finished_at: datetime | None = None
    events: list[ChatRunEventRead] = Field(default_factory=list)


class ChatSessionRead(ChatSessionSummaryRead):
    messages: list[ChatMessageRead] = Field(default_factory=list)
    documents: list[UploadedDocumentRead] = Field(default_factory=list)
    runs: list[ChatRunRead] = Field(default_factory=list)


class ChatSessionListResponse(ORMModel):
    items: list[ChatSessionSummaryRead] = Field(default_factory=list)


class ChatSessionCreateRequest(ORMModel):
    title: str | None = None


class ChatSessionCreateResponse(ORMModel):
    session: ChatSessionSummaryRead


class ChatSendMessageResponse(ORMModel):
    session: ChatSessionRead
    run: ChatRunRead
