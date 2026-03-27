from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.services.bootstrap_service import bootstrap_defaults
from app.services.database_service import initialize_database

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.DEBUG)
    database_status = initialize_database()
    with SessionLocal() as session:
        created_tools, created_agents = bootstrap_defaults(session)
    logger.info(
        "Starting %s in %s mode with SQLite at %s (bootstrapped tools=%s agents=%s)",
        settings.APP_NAME,
        settings.APP_ENV,
        database_status.sqlite_path,
        created_tools,
        created_agents,
    )
    yield
    logger.info("Shutting down %s", settings.APP_NAME)
