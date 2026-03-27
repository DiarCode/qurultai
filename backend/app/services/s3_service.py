from __future__ import annotations

from datetime import timedelta

from app.core.config import get_settings
from app.core.integrations import get_minio_client


def ensure_bucket() -> None:
    settings = get_settings()
    client = get_minio_client()
    if not client.bucket_exists(settings.MINIO_BUCKET):
        client.make_bucket(settings.MINIO_BUCKET)


def upload_bytes(object_key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
    from io import BytesIO

    settings = get_settings()
    ensure_bucket()
    client = get_minio_client()

    client.put_object(
        bucket_name=settings.MINIO_BUCKET,
        object_name=object_key,
        data=BytesIO(data),
        length=len(data),
        content_type=content_type,
    )
    return object_key


def upload_text(object_key: str, text: str, content_type: str = "text/plain") -> str:
    return upload_bytes(object_key, text.encode("utf-8"), content_type=content_type)


def delete_object(object_key: str) -> None:
    settings = get_settings()
    client = get_minio_client()
    try:
        client.remove_object(settings.MINIO_BUCKET, object_key)
    except Exception:
        return


def object_exists(object_key: str) -> bool:
    settings = get_settings()
    client = get_minio_client()
    try:
        client.stat_object(settings.MINIO_BUCKET, object_key)
        return True
    except Exception:
        return False


def make_presigned_get_url(object_key: str, expires_hours: int = 24) -> str | None:
    settings = get_settings()
    client = get_minio_client()
    try:
        return client.presigned_get_object(
            settings.MINIO_BUCKET,
            object_key,
            expires=timedelta(hours=expires_hours),
        )
    except Exception:
        return None


def s3_uri(object_key: str) -> str:
    settings = get_settings()
    return f"s3://{settings.MINIO_BUCKET}/{object_key}"
