from __future__ import annotations

from sqlmodel import Session, select

from app.core.exceptions import ConflictError, NotFoundError
from app.models.agent import Agent
from app.models.tool import Tool
from app.schemas.agents import AgentCreate, AgentUpdate


def _get_tools(session: Session, tool_ids: list[str]) -> list[Tool]:
    if not tool_ids:
        return []
    tools = list(session.exec(select(Tool).where(Tool.id.in_(tool_ids))))
    if len(tools) != len(set(tool_ids)):
        raise NotFoundError("One or more tool IDs were not found.")
    return tools


def create_agent(session: Session, payload: AgentCreate) -> Agent:
    existing = session.exec(select(Agent).where(Agent.key == payload.key)).first()
    if existing is not None:
        raise ConflictError(f"Agent key '{payload.key}' already exists.")

    agent = Agent(
        key=payload.key,
        name=payload.name,
        role_description=payload.role_description,
        system_prompt=payload.system_prompt,
        status=payload.status,
    )
    agent.tools = _get_tools(session, payload.tool_ids)
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent


def list_agents(session: Session) -> list[Agent]:
    return list(session.exec(select(Agent).order_by(Agent.created_at.desc())))


def get_agent(session: Session, agent_id: str) -> Agent:
    agent = session.get(Agent, agent_id)
    if agent is None:
        raise NotFoundError(f"Agent '{agent_id}' was not found.")
    return agent


def update_agent(session: Session, agent_id: str, payload: AgentUpdate) -> Agent:
    agent = get_agent(session, agent_id)
    updates = payload.model_dump(exclude_unset=True)
    tool_ids = updates.pop("tool_ids", None)

    for field_name, value in updates.items():
        setattr(agent, field_name, value)

    if tool_ids is not None:
        agent.tools = _get_tools(session, tool_ids)

    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent
