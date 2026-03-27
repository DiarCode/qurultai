from __future__ import annotations

from datetime import datetime

from sqlmodel import Session

from app.core.config import get_settings
from app.core.utils import utc_now
from app.services.database_service import DatabaseStatus, get_database_status


def get_health_snapshot(session: Session) -> tuple[datetime, DatabaseStatus]:
    return utc_now(), get_database_status(session)


def get_app_context() -> tuple[str, str, bool]:
    settings = get_settings()
    return settings.APP_NAME, settings.APP_ENV, settings.DEBUG
