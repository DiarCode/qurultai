from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import DEFAULT_API_PREFIX, SQLITE_URL_PREFIX
from app.core.utils import resolve_path


class Settings(BaseSettings):
    APP_NAME: str = "GovOrchestrator AI"
    APP_ENV: str = "local"
    DEBUG: bool = True
    API_PREFIX: str = DEFAULT_API_PREFIX
    SQLITE_DB_PATH: str = "data/sqlite/database.db"
    DATA_DIR: str = "data"
    SQLITE_DIR: str = "data/sqlite"
    UPLOADS_DIR: str = "data/uploads"
    REPORTS_DIR: str = "data/reports"
    SKILLS_DIR: str = "data/skills"
    LANGGRAPH_MAX_STEPS: int = 25

    OPENAI_API_KEY: str | None = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-5.4-nano"
    OPENAI_TEMPERATURE: float = 0.1
    OPENAI_TIMEOUT_SECONDS: float = 8.0

    QDRANT_URL: str = "http://127.0.0.1:6333"
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION: str = "room_steps"

    MINIO_ENDPOINT: str = "127.0.0.1:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET: str = "room-artifacts"
    S3_KNOWLEDGE_PREFIX: str = "knowledge"
    S3_REPORTS_PREFIX: str = "reports"

    EMBEDDING_MODEL_NAME: str = "intfloat/multilingual-e5-small"
    EMBEDDING_DIMENSION: int = 384

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def data_dir_path(self) -> Path:
        return resolve_path(self.DATA_DIR)

    @property
    def sqlite_dir_path(self) -> Path:
        return resolve_path(self.SQLITE_DIR)

    @property
    def uploads_dir_path(self) -> Path:
        return resolve_path(self.UPLOADS_DIR)

    @property
    def reports_dir_path(self) -> Path:
        return resolve_path(self.REPORTS_DIR)

    @property
    def skills_dir_path(self) -> Path:
        return resolve_path(self.SKILLS_DIR)

    @property
    def sqlite_db_path(self) -> Path:
        return resolve_path(self.SQLITE_DB_PATH)

    @property
    def sqlite_url(self) -> str:
        return f"{SQLITE_URL_PREFIX}{self.sqlite_db_path.as_posix()}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
