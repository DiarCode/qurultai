from __future__ import annotations

from app.core.config import get_settings


def get_qdrant_client():
    settings = get_settings()
    from qdrant_client import QdrantClient

    return QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)


def get_minio_client():
    settings = get_settings()
    from minio import Minio

    return Minio(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )


def get_openai_config() -> dict[str, str | float]:
    settings = get_settings()
    return {
        "base_url": settings.OPENAI_BASE_URL,
        "model": settings.OPENAI_MODEL,
        "temperature": settings.OPENAI_TEMPERATURE,
    }
