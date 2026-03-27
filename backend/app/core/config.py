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

    # MinIO / S3
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_NAME: str = "qurultai-documents"

    # Ollama / LLM
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    OLLAMA_TEMPERATURE: float = 0.3

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
