from __future__ import annotations

from typing import Any

from pydantic import Field

from app.models.enums import DocumentIndexingStatus, KnowledgeSourceStatus, KnowledgeSourceType
from app.schemas.common import AgentReference, AuditAwareResponse, ORMModel


class KnowledgeSourceCreate(ORMModel):
    key: str | None = None
    name: str
    source_type: KnowledgeSourceType
    description: str | None = None
    status: KnowledgeSourceStatus = KnowledgeSourceStatus.DRAFT
    metadata_json: dict[str, Any] = Field(default_factory=dict)
    created_by_user_id: str | None = None
    agent_ids: list[str] = Field(default_factory=list)


class KnowledgeSourceRead(AuditAwareResponse):
    key: str | None
    name: str
    source_type: KnowledgeSourceType
    description: str | None
    status: KnowledgeSourceStatus
    metadata_json: dict[str, Any]
    created_by_user_id: str | None
    linked_agents: list[AgentReference] = Field(default_factory=list)


class KnowledgeDocumentCreate(ORMModel):
    knowledge_source_id: str
    title: str
    original_filename: str
    stored_filename: str
    file_path: str
    mime_type: str
    extension: str
    checksum: str | None = None
    size_bytes: int = 0
    chunk_count: int = 0
    indexing_status: DocumentIndexingStatus = DocumentIndexingStatus.PENDING
    uploaded_by_user_id: str | None = None


class KnowledgeDocumentRead(AuditAwareResponse):
    knowledge_source_id: str
    title: str
    original_filename: str
    stored_filename: str
    file_path: str
    mime_type: str
    extension: str
    checksum: str | None
    size_bytes: int
    chunk_count: int
    indexing_status: DocumentIndexingStatus
    uploaded_by_user_id: str | None
