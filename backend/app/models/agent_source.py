from sqlmodel import Field

from app.models.common import UUIDPrimaryKeyMixin


class AgentSource(UUIDPrimaryKeyMixin, table=True):
    __tablename__ = "agent_sources"

    step_id: str = Field(foreign_key="agent_steps.id", index=True, max_length=36)
    source_type: str | None = Field(default=None, max_length=50)
    ref_id: str | None = Field(default=None)
    snippet: str | None = Field(default=None)
    score: float | None = Field(default=None, ge=0, le=1)
