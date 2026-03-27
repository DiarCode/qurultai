from __future__ import annotations

from uuid import uuid4

from app.core.config import get_settings
from app.core.integrations import get_qdrant_client
from app.services.embedding_service import embed_query, embed_texts


def _collection_name() -> str:
    return get_settings().QDRANT_COLLECTION


def ensure_collection() -> None:
    settings = get_settings()
    client = get_qdrant_client()

    try:
        client.get_collection(_collection_name())
        return
    except Exception:
        pass

    from qdrant_client.http import models as rest

    client.create_collection(
        collection_name=_collection_name(),
        vectors_config=rest.VectorParams(size=settings.EMBEDDING_DIMENSION, distance=rest.Distance.COSINE),
    )


def ingest_document_chunks(document_id: str, agent_id: str | None, chunks: list[str], s3_key: str) -> int:
    if not chunks:
        return 0

    ensure_collection()
    client = get_qdrant_client()
    vectors = embed_texts(chunks)

    from qdrant_client.http import models as rest

    points = []
    for chunk, vector in zip(chunks, vectors, strict=False):
        points.append(
            rest.PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload={
                    "document_id": document_id,
                    "agent_id": agent_id,
                    "text": chunk,
                    "s3_key": s3_key,
                },
            )
        )

    client.upsert(collection_name=_collection_name(), points=points)
    return len(points)


def delete_document_points(document_id: str) -> None:
    ensure_collection()
    client = get_qdrant_client()

    from qdrant_client.http import models as rest

    selector = rest.FilterSelector(
        filter=rest.Filter(
            must=[rest.FieldCondition(key="document_id", match=rest.MatchValue(value=document_id))]
        )
    )
    client.delete(collection_name=_collection_name(), points_selector=selector)


def search(query: str, limit: int = 5, agent_id: str | None = None) -> list[dict[str, str | float | None]]:
    ensure_collection()
    client = get_qdrant_client()
    vector = embed_query(query)

    from qdrant_client.http import models as rest

    query_filter = None
    if agent_id:
        query_filter = rest.Filter(
            must=[rest.FieldCondition(key="agent_id", match=rest.MatchValue(value=agent_id))]
        )

    results = client.search(
        collection_name=_collection_name(),
        query_vector=vector,
        limit=limit,
        query_filter=query_filter,
    )

    payload: list[dict[str, str | float | None]] = []
    for hit in results:
        data = hit.payload or {}
        payload.append(
            {
                "document_id": str(data.get("document_id") or ""),
                "agent_id": str(data.get("agent_id") or "") if data.get("agent_id") else None,
                "text": str(data.get("text") or ""),
                "s3_key": str(data.get("s3_key") or ""),
                "score": float(hit.score or 0.0),
            }
        )

    return payload
