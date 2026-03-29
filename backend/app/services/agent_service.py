from __future__ import annotations

import re

from sqlmodel import Session, select

from app.core.exceptions import ConflictError, NotFoundError
from app.models.agent import Agent
from app.models.knowledge_document import AgentKnowledgeLink, KnowledgeDocument
from app.models.skill import Skill
from app.models.tool import Tool
from app.schemas.agents import AgentCreate, AgentUpdate


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "agent"


def _generate_unique_key(session: Session, name: str) -> str:
    base = _slugify(name)
    candidate = base
    suffix = 2
    while session.exec(select(Agent).where(Agent.key == candidate)).first() is not None:
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate


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


def create_agent(session: Session, payload: AgentCreate) -> Agent:
    key = payload.key or _generate_unique_key(session, payload.name)
    existing = session.exec(select(Agent).where(Agent.key == key)).first()
    if existing is not None:
        raise ConflictError(f"Agent key '{key}' already exists.")

    agent = Agent(
        key=key,
        name=payload.name,
        role_description=payload.role or payload.role_description or payload.name,
        description=payload.description,
        system_prompt=payload.system_prompt,
        goals_json=payload.goals,
        constraints_json=payload.constraints,
        status=payload.status,
    )
    agent.tools = _get_tools(session, payload.tool_ids)
    agent.skills = _get_skills(session, payload.skill_ids)
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

    if "role" in updates:
        updates["role_description"] = updates.pop("role")
    if "role_description" in updates:
        updates["role_description"] = updates["role_description"]
    if "goals" in updates:
        updates["goals_json"] = updates.pop("goals")
    if "constraints" in updates:
        updates["constraints_json"] = updates.pop("constraints")
    if "key" in updates and updates["key"] != agent.key:
        duplicate = session.exec(select(Agent).where(Agent.key == updates["key"])).first()
        if duplicate is not None:
            raise ConflictError(f"Agent key '{updates['key']}' already exists.")

    for field_name, value in updates.items():
        setattr(agent, field_name, value)

    if tool_ids is not None:
        agent.tools = _get_tools(session, tool_ids)
    if skill_ids is not None:
        agent.skills = _get_skills(session, skill_ids)

    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent


def delete_agent(session: Session, agent_id: str) -> None:
    agent = get_agent(session, agent_id)

    links = list(
        session.exec(select(AgentKnowledgeLink).where(AgentKnowledgeLink.agent_id == agent_id))
    )
    for link in links:
        session.delete(link)

    session.delete(agent)
    session.commit()


def list_agent_tools(session: Session, agent_id: str) -> list[Tool]:
    agent = get_agent(session, agent_id)
    return list(agent.tools)


def add_agent_tool(session: Session, agent_id: str, tool_id: str) -> Agent:
    agent = get_agent(session, agent_id)
    tool = session.get(Tool, tool_id)
    if tool is None:
        raise NotFoundError(f"Tool '{tool_id}' was not found.")

    if all(item.id != tool_id for item in agent.tools):
        agent.tools.append(tool)
        session.add(agent)
        session.commit()
        session.refresh(agent)
    return agent


def remove_agent_tool(session: Session, agent_id: str, tool_id: str) -> Agent:
    agent = get_agent(session, agent_id)
    agent.tools = [tool for tool in agent.tools if tool.id != tool_id]
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent


def list_agent_skills(session: Session, agent_id: str) -> list[Skill]:
    agent = get_agent(session, agent_id)
    return list(agent.skills)


def add_agent_skill(session: Session, agent_id: str, skill_id: str) -> Agent:
    agent = get_agent(session, agent_id)
    skill = session.get(Skill, skill_id)
    if skill is None:
        raise NotFoundError(f"Skill '{skill_id}' was not found.")

    if all(item.id != skill_id for item in agent.skills):
        agent.skills.append(skill)
        session.add(agent)
        session.commit()
        session.refresh(agent)
    return agent


def remove_agent_skill(session: Session, agent_id: str, skill_id: str) -> Agent:
    agent = get_agent(session, agent_id)
    agent.skills = [skill for skill in agent.skills if skill.id != skill_id]
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent


def list_agent_documents(session: Session, agent_id: str) -> list[KnowledgeDocument]:
    get_agent(session, agent_id)
    links = list(
        session.exec(select(AgentKnowledgeLink).where(AgentKnowledgeLink.agent_id == agent_id))
    )
    if not links:
        return []
    document_ids = [link.document_id for link in links]
    return list(
        session.exec(
            select(KnowledgeDocument)
            .where(KnowledgeDocument.id.in_(document_ids))
            .order_by(KnowledgeDocument.created_at.desc())
        )
    )


def link_document_to_agent(session: Session, agent_id: str, document_id: str) -> None:
    get_agent(session, agent_id)
    doc = session.get(KnowledgeDocument, document_id)
    if doc is None:
        raise NotFoundError(f"Knowledge document '{document_id}' was not found.")

    existing = session.exec(
        select(AgentKnowledgeLink).where(
            AgentKnowledgeLink.agent_id == agent_id,
            AgentKnowledgeLink.document_id == document_id,
        )
    ).first()
    if existing is None:
        session.add(AgentKnowledgeLink(agent_id=agent_id, document_id=document_id))
        session.commit()


def unlink_document_from_agent(session: Session, agent_id: str, document_id: str) -> None:
    get_agent(session, agent_id)
    link = session.exec(
        select(AgentKnowledgeLink).where(
            AgentKnowledgeLink.agent_id == agent_id,
            AgentKnowledgeLink.document_id == document_id,
        )
    ).first()
    if link is not None:
        session.delete(link)
        session.commit()
