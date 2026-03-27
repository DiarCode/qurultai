from __future__ import annotations

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import UserRole

if TYPE_CHECKING:
    from app.models.agent import Agent
    from app.models.audit_log import AuditLog
    from app.models.case import Case
    from app.models.knowledge_document import KnowledgeDocument
    from app.models.knowledge_source import KnowledgeSource


class User(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    __tablename__ = "users"

    email: str = Field(index=True, unique=True, max_length=320)
    full_name: str = Field(max_length=255)
    password_hash: str = Field(max_length=255)
    role: UserRole = Field(default=UserRole.ANALYST, max_length=50)
    is_active: bool = Field(default=True)

    owned_agents: list["Agent"] = Relationship(back_populates="owner")
    created_knowledge_sources: list["KnowledgeSource"] = Relationship(back_populates="created_by")
    uploaded_documents: list["KnowledgeDocument"] = Relationship(back_populates="uploaded_by")
    submitted_cases: list["Case"] = Relationship(back_populates="submitted_by")
    audit_logs: list["AuditLog"] = Relationship(back_populates="actor")
