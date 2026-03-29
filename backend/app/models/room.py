from sqlalchemy import JSON
from sqlmodel import Field

from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class Room(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    __tablename__ = "rooms"

    title: str = Field(default="New chat", max_length=255, index=True)
    status: str = Field(default="active", max_length=50, index=True)
    initial_query: str = Field(default="")
    last_message_preview: str | None = Field(default=None, max_length=280)
    context_text: str | None = Field(default=None)
    mission_goals_json: list[str] = Field(default_factory=list, sa_type=JSON)
    final_report_md: str | None = Field(default=None)
