from __future__ import annotations

from sqlmodel import Session, select

from app.core.exceptions import ConflictError, NotFoundError
from app.models.agent import Agent
from app.models.tool import AgentToolLink, Tool


def create_tool(
    session: Session,
    name: str,
    description: str | None,
    tool_type: str,
    input_schema_json: dict | None = None,
    output_schema_json: dict | None = None,
    configuration_json: dict | None = None,
    endpoint_url: str | None = None,
) -> Tool:
    existing = session.exec(select(Tool).where(Tool.name == name)).first()
    if existing is not None:
        raise ConflictError(f"Tool name '{name}' already exists.")

    tool = Tool(
        name=name,
        description=description,
        tool_type=tool_type,
        input_schema_json=input_schema_json or {},
        output_schema_json=output_schema_json or {},
        configuration_json=configuration_json or {},
        endpoint_url=endpoint_url,
    )
    session.add(tool)
    session.commit()
    session.refresh(tool)
    return tool


def list_tools(session: Session) -> list[Tool]:
    return list(session.exec(select(Tool).order_by(Tool.created_at.desc())))


def get_tool(session: Session, tool_id: str) -> Tool:
    tool = session.get(Tool, tool_id)
    if tool is None:
        raise NotFoundError(f"Tool '{tool_id}' was not found.")
    return tool


def update_tool(
    session: Session,
    tool_id: str,
    name: str | None = None,
    description: str | None = None,
    tool_type: str | None = None,
    input_schema_json: dict | None = None,
    output_schema_json: dict | None = None,
    configuration_json: dict | None = None,
    endpoint_url: str | None = None,
) -> Tool:
    tool = get_tool(session, tool_id)

    if name is not None:
        tool.name = name
    if description is not None:
        tool.description = description
    if tool_type is not None:
        tool.tool_type = tool_type
    if input_schema_json is not None:
        tool.input_schema_json = input_schema_json
    if output_schema_json is not None:
        tool.output_schema_json = output_schema_json
    if configuration_json is not None:
        tool.configuration_json = configuration_json
    if endpoint_url is not None:
        tool.endpoint_url = endpoint_url

    session.add(tool)
    session.commit()
    session.refresh(tool)
    return tool


def delete_tool(session: Session, tool_id: str) -> None:
    tool = get_tool(session, tool_id)
    session.delete(tool)
    session.commit()


def attach_tools_to_agent(
    session: Session,
    agent_id: str,
    tool_ids: list[str],
    config_overrides: dict[str, dict] | None = None,
) -> Agent:
    agent = session.get(Agent, agent_id)
    if agent is None:
        raise NotFoundError(f"Agent '{agent_id}' was not found.")

    existing_tool_ids = {t.id for t in agent.tools}
    overrides = config_overrides or {}

    for tool_id in tool_ids:
        if tool_id in existing_tool_ids:
            continue
        _ = get_tool(session, tool_id)

        link = AgentToolLink(
            agent_id=agent_id,
            tool_id=tool_id,
            config_override_json=overrides.get(tool_id, {}),
        )
        session.add(link)

    session.commit()
    session.refresh(agent)
    return agent


def detach_tools_from_agent(
    session: Session, agent_id: str, tool_ids: list[str]
) -> Agent:
    agent = session.get(Agent, agent_id)
    if agent is None:
        raise NotFoundError(f"Agent '{agent_id}' was not found.")

    agent.tools = [t for t in agent.tools if t.id not in tool_ids]

    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent


def get_agent_tools(session: Session, agent_id: str) -> list[dict]:
    agent = session.get(Agent, agent_id)
    if agent is None:
        raise NotFoundError(f"Agent '{agent_id}' was not found.")

    results = []
    for tool in agent.tools:
        link = session.exec(
            select(AgentToolLink).where(
                AgentToolLink.agent_id == agent_id,
                AgentToolLink.tool_id == tool.id,
            )
        ).first()
        results.append({
            "tool_id": tool.id,
            "name": tool.name,
            "tool_type": tool.tool_type,
            "description": tool.description,
            "input_schema": tool.input_schema_json,
            "output_schema": tool.output_schema_json,
            "configuration": tool.configuration_json,
            "config_override": link.config_override_json if link else {},
        })
    return results
