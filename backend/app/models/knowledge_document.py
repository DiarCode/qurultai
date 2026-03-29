from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, UniqueConstraint
from sqlmodel import Field, SQLModel

from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class AgentKnowledgeLink(SQLModel, table=True):
    __tablename__ = "agent_knowledge_documents"
    __table_args__ = (UniqueConstraint("agent_id", "document_id", name="uq_agent_document_link"),)

    agent_id: str = Field(foreign_key="agents.id", primary_key=True, max_length=36)
    document_id: str = Field(foreign_key="knowledge_documents.id", primary_key=True, max_length=36)


class KnowledgeDocument(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    __tablename__ = "knowledge_documents"

    title: str = Field(max_length=255)
    source_filename: str = Field(max_length=255)
    mime_type: str | None = Field(default=None, max_length=120)
    size_bytes: int = Field(default=0, ge=0)
    s3_bucket: str = Field(max_length=255)
    s3_key: str = Field(max_length=1024, unique=True)
    text_preview: str | None = Field(default=None)
    metadata_json: dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
