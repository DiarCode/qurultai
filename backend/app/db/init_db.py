from __future__ import annotations

from app.db.base import SQLModel
from app.db.engine import engine


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
