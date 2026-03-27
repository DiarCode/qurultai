from __future__ import annotations

from sqlmodel import Session

from app.schemas.agents import AgentCreate, AgentRead, AgentUpdate
from app.services import agent_service


def create_agent(session: Session, payload: AgentCreate) -> AgentRead:
    return AgentRead.model_validate(agent_service.create_agent(session, payload))


def list_agents(session: Session) -> list[AgentRead]:
    return [AgentRead.model_validate(agent) for agent in agent_service.list_agents(session)]


def get_agent(session: Session, agent_id: str) -> AgentRead:
    return AgentRead.model_validate(agent_service.get_agent(session, agent_id))


def update_agent(session: Session, agent_id: str, payload: AgentUpdate) -> AgentRead:
    return AgentRead.model_validate(agent_service.update_agent(session, agent_id, payload))
