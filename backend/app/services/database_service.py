from __future__ import annotations

from dataclasses import dataclass

from sqlmodel import Session

from app.core.config import get_settings
from app.core.utils import ensure_directory
from app.db.init_db import init_db


@dataclass(slots=True)
class DatabaseStatus:
    ready: bool
    sqlite_path: str
    wal_mode: str
    foreign_keys: bool


def ensure_runtime_directories() -> None:
    settings = get_settings()
    ensure_directory(settings.data_dir_path)
    ensure_directory(settings.sqlite_dir_path)
    ensure_directory(settings.uploads_dir_path)
    ensure_directory(settings.reports_dir_path)
    ensure_directory(settings.skills_dir_path)


def initialize_database() -> DatabaseStatus:
    ensure_runtime_directories()
    init_db()
    settings = get_settings()
    return DatabaseStatus(
        ready=True,
        sqlite_path=str(settings.sqlite_db_path),
        wal_mode="wal",
        foreign_keys=True,
    )


def get_database_status(session: Session) -> DatabaseStatus:
    connection = session.connection()
    wal_mode = str(connection.exec_driver_sql("PRAGMA journal_mode;").scalar_one())
    foreign_keys_value = int(connection.exec_driver_sql("PRAGMA foreign_keys;").scalar_one())
    settings = get_settings()
    return DatabaseStatus(
        ready=bool(connection.exec_driver_sql("SELECT 1;").scalar_one()),
        sqlite_path=str(settings.sqlite_db_path),
        wal_mode=wal_mode,
        foreign_keys=foreign_keys_value == 1,
    )
