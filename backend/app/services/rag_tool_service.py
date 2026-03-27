from __future__ import annotations

from app.services import qdrant_service


def rag_search(query: str, limit: int = 5, agent_id: str | None = None) -> list[dict[str, str | float | None]]:
    try:
        return qdrant_service.search(query=query, limit=limit, agent_id=agent_id)
    except Exception:
        return []
