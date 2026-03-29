from __future__ import annotations

from datetime import timedelta
from pathlib import Path

from app.core.config import get_settings
from app.core.integrations import get_minio_client
from app.core.utils import ensure_directory


def _local_object_path(object_key: str) -> Path:
    settings = get_settings()
    object_store_dir = ensure_directory(settings.data_dir_path / "object_store")
    path = object_store_dir / object_key
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def ensure_bucket() -> None:
    settings = get_settings()
    try:
        client = get_minio_client()
        if not client.bucket_exists(settings.MINIO_BUCKET):
            client.make_bucket(settings.MINIO_BUCKET)
    except Exception:
        return


def upload_bytes(
    object_key: str, data: bytes, content_type: str = "application/octet-stream"
) -> str:
    from io import BytesIO

    settings = get_settings()
    try:
        ensure_bucket()
        client = get_minio_client()
        client.put_object(
            bucket_name=settings.MINIO_BUCKET,
            object_name=object_key,
            data=BytesIO(data),
            length=len(data),
            content_type=content_type,
        )
    except Exception:
        _local_object_path(object_key).write_bytes(data)
    return object_key


def upload_text(object_key: str, text: str, content_type: str = "text/plain") -> str:
    return upload_bytes(object_key, text.encode("utf-8"), content_type=content_type)


def download_bytes(object_key: str) -> bytes:
    settings = get_settings()
    try:
        client = get_minio_client()
        response = client.get_object(settings.MINIO_BUCKET, object_key)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()
    except Exception:
        return _local_object_path(object_key).read_bytes()


def delete_object(object_key: str) -> None:
    settings = get_settings()
    try:
        client = get_minio_client()
        client.remove_object(settings.MINIO_BUCKET, object_key)
    except Exception:
        path = _local_object_path(object_key)
        path.unlink(missing_ok=True)


def object_exists(object_key: str) -> bool:
    settings = get_settings()
    try:
        client = get_minio_client()
        client.stat_object(settings.MINIO_BUCKET, object_key)
        return True
    except Exception:
        return _local_object_path(object_key).exists()


def make_presigned_get_url(object_key: str, expires_hours: int = 24) -> str | None:
    settings = get_settings()
    try:
        client = get_minio_client()
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
