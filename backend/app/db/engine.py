from __future__ import annotations

import sqlite3
from pathlib import Path

from sqlalchemy import event
from sqlmodel import create_engine

from app.core.config import get_settings
from app.core.utils import ensure_directory

settings = get_settings()


def _prepare_sqlite_file() -> Path:
    ensure_directory(settings.sqlite_dir_path)
    db_path = settings.sqlite_db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.touch(exist_ok=True)
    return db_path


_prepare_sqlite_file()

engine = create_engine(
    settings.sqlite_url,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragmas(dbapi_connection: sqlite3.Connection, _connection_record: object) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    cursor.close()
