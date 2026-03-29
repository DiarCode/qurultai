from __future__ import annotations

from uuid import uuid4

from app.core.config import get_settings
from app.core.integrations import get_qdrant_client
from app.services.embedding_service import embed_query, embed_texts


def _coerce_optional_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, (int, str)):
        return int(value)
    return None


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
        vectors_config=rest.VectorParams(
            size=settings.EMBEDDING_DIMENSION, distance=rest.Distance.COSINE
        ),
    )


def ingest_document_chunks(
    document_id: str,
    agent_id: str | None,
    chunks: list[str],
    s3_key: str,
    *,
    title: str | None = None,
    mime_type: str | None = None,
) -> int:
    if not chunks:
        return 0

    ensure_collection()
    client = get_qdrant_client()
    vectors = embed_texts(chunks)

    from qdrant_client.http import models as rest

    points = []
    chunk_count = len(chunks)
    for index, (chunk, vector) in enumerate(zip(chunks, vectors, strict=False), start=1):
        points.append(
            rest.PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload={
                    "document_id": document_id,
                    "agent_id": agent_id,
                    "title": title,
                    "mime_type": mime_type,
                    "text": chunk,
                    "s3_key": s3_key,
                    "chunk_index": index,
                    "chunk_count": chunk_count,
                    "location": f"Chunk {index} of {chunk_count}",
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


def search(
    query: str,
    limit: int = 5,
    agent_id: str | None = None,
) -> list[dict[str, str | float | int | None]]:
    ensure_collection()
    client = get_qdrant_client()
    vector = embed_query(query)

    from qdrant_client.http import models as rest

    query_filter = None
    if agent_id:
        query_filter = rest.Filter(
            must=[rest.FieldCondition(key="agent_id", match=rest.MatchValue(value=agent_id))]
        )

    if hasattr(client, "search"):
        results = client.search(
            collection_name=_collection_name(),
            query_vector=vector,
            limit=limit,
            query_filter=query_filter,
        )
    else:
        query_response = client.query_points(
            collection_name=_collection_name(),
            query=vector,
            limit=limit,
            query_filter=query_filter,
        )
        results = getattr(query_response, "points", query_response)

    payload: list[dict[str, str | float | None]] = []
    for hit in results:
        data = hit.payload or {}
        payload.append(
            {
                "document_id": str(data.get("document_id") or ""),
                "agent_id": str(data.get("agent_id") or "") if data.get("agent_id") else None,
                "title": str(data.get("title") or "") if data.get("title") else None,
                "mime_type": str(data.get("mime_type") or "") if data.get("mime_type") else None,
                "text": str(data.get("text") or ""),
                "s3_key": str(data.get("s3_key") or ""),
                "score": float(hit.score or 0.0),
                "chunk_index": _coerce_optional_int(data.get("chunk_index")),
                "chunk_count": _coerce_optional_int(data.get("chunk_count")),
                "location": str(data.get("location") or "") if data.get("location") else None,
            }
        )

    return payload
