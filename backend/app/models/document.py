from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.core.utils import utc_now
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.agent import Agent


class AgentDocumentLink(SQLModel, table=True):
    __tablename__ = "agent_documents"
    __table_args__ = (UniqueConstraint("agent_id", "document_id", name="uq_agent_document"),)

    agent_id: str = Field(foreign_key="agents.id", primary_key=True, max_length=36)
    document_id: str = Field(foreign_key="documents.id", primary_key=True, max_length=36)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)


class Document(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    __tablename__ = "documents"

    filename: str = Field(max_length=512)
    original_filename: str = Field(max_length=512)
    content_type: str = Field(max_length=255)
    file_size: int = Field(default=0)
    bucket_name: str = Field(max_length=255)
    object_key: str = Field(max_length=1024, unique=True)
    description: str | None = Field(default=None)

    agents: list["Agent"] = Relationship(
        back_populates="documents", link_model=AgentDocumentLink
    )
