from __future__ import annotations

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AudienceMode, ReportStatus

if TYPE_CHECKING:
    from app.models.case import Case


class Report(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    __tablename__ = "reports"

    case_id: str = Field(foreign_key="cases.id", index=True, max_length=36)
    orchestration_run_id: str | None = Field(
        default=None,
        foreign_key="orchestration_runs.id",
        index=True,
        max_length=36,
    )
    audience_mode: AudienceMode = Field(max_length=50)
    title: str = Field(max_length=255)
    summary: str = Field()
    markdown_content: str = Field()
    html_path: str | None = Field(default=None, max_length=1024)
    pdf_path: str | None = Field(default=None, max_length=1024)
    status: ReportStatus = Field(default=ReportStatus.DRAFT, max_length=50)

    case: "Case" = Relationship(back_populates="reports")
