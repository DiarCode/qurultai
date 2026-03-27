from __future__ import annotations

from pydantic import Base64Bytes
from pydantic import Field

from app.schemas.common import AuditAwareResponse, ORMModel


class KnowledgeDocumentUploadRequest(ORMModel):
    source_filename: str
    mime_type: str = "application/octet-stream"
    content_base64: Base64Bytes | None = None
    plain_text: str | None = None
    agent_id: str | None = None
    title: str | None = None


class KnowledgeDocumentRead(AuditAwareResponse):
    title: str
    source_filename: str
    mime_type: str | None
    size_bytes: int
    s3_bucket: str
    s3_key: str
    text_preview: str | None
    metadata_json: dict[str, str] = Field(default_factory=dict)
    agent_ids: list[str] = Field(default_factory=list)


class KnowledgeDocumentUploadResponse(ORMModel):
    document: KnowledgeDocumentRead
    chunks_ingested: int


class KnowledgeDocumentListResponse(ORMModel):
    items: list[KnowledgeDocumentRead] = Field(default_factory=list)


class KnowledgeSearchRequest(ORMModel):
    query: str
    limit: int = 5
    agent_id: str | None = None


class KnowledgeSearchHit(ORMModel):
    document_id: str
    agent_id: str | None = None
    text: str
    s3_key: str
    score: float


class KnowledgeSearchResponse(ORMModel):
    items: list[KnowledgeSearchHit] = Field(default_factory=list)


class KnowledgeDocumentDownloadResponse(ORMModel):
    document_id: str
    s3_uri: str
    presigned_url: str | None = None
