from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path


def utc_now() -> datetime:
    return datetime.now(UTC)


def resolve_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return Path.cwd() / path


def ensure_directory(path_value: str | Path) -> Path:
    path = resolve_path(path_value)
    path.mkdir(parents=True, exist_ok=True)
    return path
