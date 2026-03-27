from __future__ import annotations

from pydantic import Field

from app.schemas.common import AuditAwareResponse, ORMModel


class DocumentRead(AuditAwareResponse):
    filename: str
    original_filename: str
    content_type: str
    file_size: int
    bucket_name: str
    object_key: str
    description: str | None


class DocumentDeleteRequest(ORMModel):
    document_ids: list[str]


class DocumentDeleteResponse(ORMModel):
    deleted_count: int


class AgentDocumentRequest(ORMModel):
    document_ids: list[str] = Field(min_length=1)
