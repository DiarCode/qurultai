from __future__ import annotations

from sqlmodel import Session, select

from app.models.agent import Agent
from app.services.kz_government_catalog import ensure_tools, seed_kz_government_catalog


def bootstrap_defaults(session: Session) -> tuple[int, int]:
    _, created_tools = ensure_tools(session)
    existing_agents = session.exec(select(Agent.id)).first()
    created_agents = 0
    if existing_agents is None:
        summary = seed_kz_government_catalog(session, replace_existing_agents=False)
        created_agents = summary["created_agents"]
    else:
        session.commit()
    return created_tools, created_agents
