from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON
from sqlmodel import Field, Relationship

from app.models.common import UUIDPrimaryKeyMixin
from app.models.enums import RunStatus

if TYPE_CHECKING:
    from app.models.case import Case


class OrchestrationRun(UUIDPrimaryKeyMixin, table=True):
    __tablename__ = "orchestration_runs"

    case_id: str = Field(foreign_key="cases.id", index=True, max_length=36)
    graph_version: str = Field(max_length=100)
    status: RunStatus = Field(default=RunStatus.PENDING, max_length=50)
    selected_agents_json: list[str] = Field(default_factory=list, sa_type=JSON)
    started_at: datetime | None = Field(default=None)
    finished_at: datetime | None = Field(default=None)
    duration_ms: int | None = Field(default=None, ge=0)
    error_message: str | None = Field(default=None)
    final_report_id: str | None = Field(default=None, foreign_key="reports.id", index=True, max_length=36)

    case: "Case" = Relationship(back_populates="orchestration_runs")
