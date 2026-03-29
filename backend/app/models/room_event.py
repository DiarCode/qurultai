from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, UniqueConstraint
from sqlmodel import Field, SQLModel

from app.core.utils import utc_now
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class RoomDocumentLink(SQLModel, table=True):
    __tablename__ = "room_documents"
    __table_args__ = (UniqueConstraint("room_id", "document_id", name="uq_room_document"),)

    room_id: str = Field(foreign_key="rooms.id", primary_key=True, max_length=36)
    document_id: str = Field(foreign_key="knowledge_documents.id", primary_key=True, max_length=36)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)


class RoomEvent(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    __tablename__ = "room_events"
    __table_args__ = (UniqueConstraint("room_id", "sequence", name="uq_room_event_sequence"),)

    room_id: str = Field(foreign_key="rooms.id", index=True, max_length=36)
    sequence: int = Field(index=True, ge=1)
    event_type: str = Field(index=True, max_length=80)
    payload_json: dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
