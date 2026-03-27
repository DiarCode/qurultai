from __future__ import annotations

from sqlmodel import Session, select

from app.core.exceptions import ConflictError, NotFoundError
from app.models.agent import Agent
from app.models.knowledge_document import AgentKnowledgeLink, KnowledgeDocument
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


def delete_agent(session: Session, agent_id: str) -> None:
    agent = get_agent(session, agent_id)

    links = list(session.exec(select(AgentKnowledgeLink).where(AgentKnowledgeLink.agent_id == agent_id)))
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


def list_agent_documents(session: Session, agent_id: str) -> list[KnowledgeDocument]:
    get_agent(session, agent_id)
    links = list(session.exec(select(AgentKnowledgeLink).where(AgentKnowledgeLink.agent_id == agent_id)))
    if not links:
        return []
    docs = list(
        session.exec(
            select(KnowledgeDocument)
            .where(KnowledgeDocument.id.in_([link.document_id for link in links]))
            .order_by(KnowledgeDocument.created_at.desc())
        )
    )
    for doc in docs:
        setattr(doc, "agent_ids", [agent_id])
    return docs


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
