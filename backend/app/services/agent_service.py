from __future__ import annotations

from sqlmodel import Session, select

from app.core.exceptions import ConflictError, NotFoundError
from app.models.agent import Agent
from app.models.document import Document
from app.models.skill import Skill
from app.models.tool import Tool
from app.schemas.agents import AgentCreate, AgentUpdate


def _get_tools(session: Session, tool_ids: list[str]) -> list[Tool]:
    if not tool_ids:
        return []
    tools = list(session.exec(select(Tool).where(Tool.id.in_(tool_ids))))
    if len(tools) != len(set(tool_ids)):
        raise NotFoundError("One or more tool IDs were not found.")
    return tools


def _get_skills(session: Session, skill_ids: list[str]) -> list[Skill]:
    if not skill_ids:
        return []
    skills = list(session.exec(select(Skill).where(Skill.id.in_(skill_ids))))
    if len(skills) != len(set(skill_ids)):
        raise NotFoundError("One or more skill IDs were not found.")
    return skills


def _get_documents(session: Session, document_ids: list[str]) -> list[Document]:
    if not document_ids:
        return []
    docs = list(session.exec(select(Document).where(Document.id.in_(document_ids))))
    if len(docs) != len(set(document_ids)):
        raise NotFoundError("One or more document IDs were not found.")
    return docs


def create_agent(session: Session, payload: AgentCreate) -> Agent:
    existing = session.exec(select(Agent).where(Agent.key == payload.key)).first()
    if existing is not None:
        raise ConflictError(f"Agent key '{payload.key}' already exists.")

    agent = Agent(
        key=payload.key,
        name=payload.name,
        role_description=payload.role_description,
        system_prompt=payload.system_prompt,
        goals_json=payload.goals_json,
        constraints_json=payload.constraints_json,
        status=payload.status,
    )
    agent.tools = _get_tools(session, payload.tool_ids)
    agent.skills = _get_skills(session, payload.skill_ids)
    agent.documents = _get_documents(session, payload.document_ids)
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
    skill_ids = updates.pop("skill_ids", None)
    document_ids = updates.pop("document_ids", None)

    for field_name, value in updates.items():
        setattr(agent, field_name, value)

    if tool_ids is not None:
        agent.tools = _get_tools(session, tool_ids)
    if skill_ids is not None:
        agent.skills = _get_skills(session, skill_ids)
    if document_ids is not None:
        agent.documents = _get_documents(session, document_ids)

    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent
