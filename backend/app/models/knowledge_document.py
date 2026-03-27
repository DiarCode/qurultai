from __future__ import annotations

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import DocumentIndexingStatus

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.knowledge_source import KnowledgeSource
    from app.models.user import User


class KnowledgeDocument(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    __tablename__ = "knowledge_documents"

    knowledge_source_id: str = Field(foreign_key="knowledge_sources.id", index=True, max_length=36)
    title: str = Field(max_length=255)
    original_filename: str = Field(max_length=255)
    stored_filename: str = Field(max_length=255)
    file_path: str = Field(max_length=1024)
    mime_type: str = Field(max_length=150)
    extension: str = Field(max_length=50)
    checksum: str | None = Field(default=None, max_length=255)
    size_bytes: int = Field(default=0, ge=0)
    chunk_count: int = Field(default=0, ge=0)
    indexing_status: DocumentIndexingStatus = Field(
        default=DocumentIndexingStatus.PENDING,
        max_length=50,
    )
    uploaded_by_user_id: str | None = Field(default=None, foreign_key="users.id", index=True, max_length=36)

    knowledge_source: "KnowledgeSource" = Relationship(back_populates="documents")
    uploaded_by: "User | None" = Relationship(back_populates="uploaded_documents")
    related_cases: list["Case"] = Relationship(back_populates="source_document")
