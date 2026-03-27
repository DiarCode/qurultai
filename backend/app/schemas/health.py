from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class DatabaseHealthResponse(BaseModel):
    ready: bool
    sqlite_path: str
    wal_mode: str
    foreign_keys: bool


class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str
    debug: bool
    timestamp: datetime
    database: DatabaseHealthResponse
