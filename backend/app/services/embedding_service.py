from __future__ import annotations

import hashlib
from functools import lru_cache

from app.core.config import get_settings


def _hash_embedding(text: str, dim: int) -> list[float]:
    digest = hashlib.sha256(text.encode("utf-8", errors="ignore")).digest()
    values = list(digest)
    repeated = (values * ((dim // len(values)) + 1))[:dim]
    return [value / 255.0 for value in repeated]


@lru_cache(maxsize=1)
def _load_sentence_transformer():
    settings = get_settings()
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.EMBEDDING_MODEL_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    settings = get_settings()
    if not texts:
        return []

    prefixed = [f"passage: {text}" for text in texts]

    try:
        model = _load_sentence_transformer()
        vectors = model.encode(prefixed, normalize_embeddings=True)
        return [vector.tolist() for vector in vectors]
    except Exception:
        return [_hash_embedding(text, settings.EMBEDDING_DIMENSION) for text in prefixed]


def embed_query(query: str) -> list[float]:
    settings = get_settings()
    prefixed = f"query: {query}"
    try:
        model = _load_sentence_transformer()
        vector = model.encode([prefixed], normalize_embeddings=True)[0]
        return vector.tolist()
    except Exception:
        return _hash_embedding(prefixed, settings.EMBEDDING_DIMENSION)
