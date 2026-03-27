from datetime import datetime
from typing import Any

from sqlalchemy import JSON
from sqlmodel import Field

from app.core.utils import utc_now
from app.models.common import UUIDPrimaryKeyMixin


class AgentStep(UUIDPrimaryKeyMixin, table=True):
    __tablename__ = "agent_steps"

    run_id: str = Field(foreign_key="agent_runs.id", index=True, max_length=36)
    step_type: str = Field(max_length=50, index=True)
    content_json: dict[str, Any] | list[Any] | str = Field(sa_type=JSON)
    tokens_used: int = Field(default=0, ge=0)
    latency_ms: float | None = Field(default=None, ge=0)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
