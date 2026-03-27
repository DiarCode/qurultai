from datetime import datetime

from sqlmodel import Field

from app.models.common import UUIDPrimaryKeyMixin


class AgentRun(UUIDPrimaryKeyMixin, table=True):
    __tablename__ = "agent_runs"

    room_id: str = Field(foreign_key="rooms.id", index=True, max_length=36)
    agent_id: str = Field(foreign_key="agents.id", index=True, max_length=36)
    status: str = Field(default="IDLE", max_length=50, index=True)
    bid_reason: str | None = Field(default=None)
    started_at: datetime | None = Field(default=None)
    finished_at: datetime | None = Field(default=None)
