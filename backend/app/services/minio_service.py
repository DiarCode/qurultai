from __future__ import annotations

import io
import logging
from functools import lru_cache

from minio import Minio
from minio.error import S3Error

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_minio_client() -> Minio:
    settings = get_settings()
    return Minio(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )


def ensure_bucket(bucket_name: str | None = None) -> str:
    settings = get_settings()
    bucket = bucket_name or settings.MINIO_BUCKET_NAME
    client = get_minio_client()
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)
        logger.info("Created MinIO bucket: %s", bucket)
    return bucket


def upload_file(
    data: bytes,
    object_key: str,
    content_type: str = "application/octet-stream",
    bucket_name: str | None = None,
) -> str:
    settings = get_settings()
    bucket = bucket_name or settings.MINIO_BUCKET_NAME
    ensure_bucket(bucket)
    client = get_minio_client()
    client.put_object(
        bucket_name=bucket,
        object_name=object_key,
        data=io.BytesIO(data),
        length=len(data),
        content_type=content_type,
    )
    logger.info("Uploaded %s to bucket %s", object_key, bucket)
    return object_key


def download_file(object_key: str, bucket_name: str | None = None) -> bytes:
    settings = get_settings()
    bucket = bucket_name or settings.MINIO_BUCKET_NAME
    client = get_minio_client()
    response = client.get_object(bucket_name=bucket, object_name=object_key)
    try:
        return response.read()
    finally:
        response.close()
        response.release_conn()


def delete_file(object_key: str, bucket_name: str | None = None) -> None:
    settings = get_settings()
    bucket = bucket_name or settings.MINIO_BUCKET_NAME
    client = get_minio_client()
    client.remove_object(bucket_name=bucket, object_name=object_key)
    logger.info("Deleted %s from bucket %s", object_key, bucket)


def delete_files(object_keys: list[str], bucket_name: str | None = None) -> None:
    for key in object_keys:
        try:
            delete_file(key, bucket_name)
        except S3Error as e:
            logger.warning("Failed to delete %s: %s", key, e)


def file_exists(object_key: str, bucket_name: str | None = None) -> bool:
    settings = get_settings()
    bucket = bucket_name or settings.MINIO_BUCKET_NAME
    client = get_minio_client()
    try:
        client.stat_object(bucket_name=bucket, object_name=object_key)
        return True
    except S3Error:
        return False
