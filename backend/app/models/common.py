from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel

from app.core.utils import utc_now


def generate_uuid() -> str:
    return str(uuid4())


class UUIDPrimaryKeyMixin(SQLModel):
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True, max_length=36)


class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"onupdate": utc_now},
        nullable=False,
    )
