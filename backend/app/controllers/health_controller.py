from __future__ import annotations

from sqlmodel import Session

from app.schemas.health import DatabaseHealthResponse, HealthResponse
from app.services.health_service import get_app_context, get_health_snapshot


def get_health(session: Session) -> HealthResponse:
    app_name, environment, debug = get_app_context()
    timestamp, database_status = get_health_snapshot(session)
    return HealthResponse(
        status="ok",
        app_name=app_name,
        environment=environment,
        debug=debug,
        timestamp=timestamp,
        database=DatabaseHealthResponse(
            ready=database_status.ready,
            sqlite_path=database_status.sqlite_path,
            wal_mode=database_status.wal_mode,
            foreign_keys=database_status.foreign_keys,
        ),
    )
