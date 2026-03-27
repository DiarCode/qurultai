from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AudienceMode, CaseRequestType, CaseStatus, InputMode

if TYPE_CHECKING:
    from app.models.case_message import CaseMessage
    from app.models.knowledge_document import KnowledgeDocument
    from app.models.orchestration_run import OrchestrationRun
    from app.models.report import Report
    from app.models.user import User


class Case(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    __tablename__ = "cases"

    title: str = Field(max_length=255)
    description: str = Field()
    request_type: CaseRequestType = Field(max_length=50)
    audience_mode: AudienceMode = Field(max_length=50)
    input_mode: InputMode = Field(max_length=50)
    status: CaseStatus = Field(default=CaseStatus.SUBMITTED, max_length=50)
    submitted_by_user_id: str | None = Field(default=None, foreign_key="users.id", index=True, max_length=36)
    source_document_id: str | None = Field(
        default=None,
        foreign_key="knowledge_documents.id",
        index=True,
        max_length=36,
    )
    completed_at: datetime | None = Field(default=None)

    submitted_by: "User | None" = Relationship(back_populates="submitted_cases")
    source_document: "KnowledgeDocument | None" = Relationship(back_populates="related_cases")
    messages: list["CaseMessage"] = Relationship(back_populates="case")
    orchestration_runs: list["OrchestrationRun"] = Relationship(back_populates="case")
    reports: list["Report"] = Relationship(back_populates="case")
