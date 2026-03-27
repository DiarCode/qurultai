from __future__ import annotations

from sqlmodel import Session

from app.schemas.agents import AgentCreate, AgentRead, AgentUpdate
from app.services import agent_service


def _to_read_model(agent) -> AgentRead:
    data = AgentRead.model_validate(agent).model_dump()
    data["tool_ids"] = [tool.id for tool in agent.tools]
    return AgentRead(**data)


def create_agent(session: Session, payload: AgentCreate) -> AgentRead:
    return _to_read_model(agent_service.create_agent(session, payload))


def list_agents(session: Session) -> list[AgentRead]:
    return [_to_read_model(agent) for agent in agent_service.list_agents(session)]


def get_agent(session: Session, agent_id: str) -> AgentRead:
    return _to_read_model(agent_service.get_agent(session, agent_id))


def update_agent(session: Session, agent_id: str, payload: AgentUpdate) -> AgentRead:
    return _to_read_model(agent_service.update_agent(session, agent_id, payload))
