from __future__ import annotations

import re
import unicodedata


def normalize_text(text: str) -> str:
    compact = " ".join(text.split())
    normalized = unicodedata.normalize("NFKC", compact)
    return normalized.strip()


def split_into_chunks(text: str, max_chars: int = 700, overlap: int = 120) -> list[str]:
    normalized = normalize_text(text)
    if not normalized:
        return []

    # Keep punctuation as soft split hints to reduce semantic drift in chunks.
    parts = re.split(r"(?<=[.!?])\s+", normalized)
    chunks: list[str] = []
    current = ""

    for part in parts:
        candidate = f"{current} {part}".strip() if current else part
        if len(candidate) <= max_chars:
            current = candidate
            continue

        if current:
            chunks.append(current)

        if len(part) <= max_chars:
            current = part
            continue

        start = 0
        while start < len(part):
            end = min(start + max_chars, len(part))
            chunks.append(part[start:end])
            if end == len(part):
                break
            start = max(0, end - overlap)
        current = ""

    if current:
        chunks.append(current)

    return [chunk for chunk in chunks if chunk]
