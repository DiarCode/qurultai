from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.services.database_service import initialize_database

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.DEBUG)
    database_status = initialize_database()
    logger.info(
        "Starting %s in %s mode with SQLite at %s",
        settings.APP_NAME,
        settings.APP_ENV,
        database_status.sqlite_path,
    )
    yield
    logger.info("Shutting down %s", settings.APP_NAME)
