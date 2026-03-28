from __future__ import annotations

from sqlmodel import Session, select

from app.models.agent import Agent
from app.models.tool import Tool

DEFAULT_TOOLS = [
    {
        "name": "rag_search",
        "description": "Retrieve relevant context snippets from indexed documents.",
        "input_schema_json": {"type": "object", "properties": {"query": {"type": "string"}}},
        "endpoint_url": None,
    },
    {
        "name": "web_search",
        "description": "Search public web sources for supporting evidence.",
        "input_schema_json": {"type": "object", "properties": {"query": {"type": "string"}}},
        "endpoint_url": None,
    },
    {
        "name": "calculator",
        "description": "Perform deterministic numeric computations.",
        "input_schema_json": {
            "type": "object",
            "properties": {
                "expression": {"type": "string"},
            },
        },
        "endpoint_url": None,
    },
]

DEFAULT_AGENTS = [
    {
        "key": "orchestrator_critic",
        "name": "Orchestrator Critic",
        "role_description": "Breaks down missions and validates consistency between specialists.",
        "system_prompt": "You decompose goals and ensure no contradictions remain in the final report.",
        "status": "active",
    },
    {
        "key": "financial_specialist",
        "name": "Financial Specialist",
        "role_description": "Analyzes budgets, ROI, costs, and forecast implications.",
        "system_prompt": "You provide fiscal analysis with explicit assumptions and risk notes.",
        "status": "active",
    },
    {
        "key": "legal_specialist",
        "name": "Legal Specialist",
        "role_description": "Assesses legal constraints, compliance risks, and policy implications.",
        "system_prompt": "You highlight legal constraints and compliance obligations.",
        "status": "active",
    },
]


def bootstrap_defaults(session: Session) -> tuple[int, int]:
    created_tools = 0
    created_agents = 0

    tools_by_name = {tool.name: tool for tool in session.exec(select(Tool))}
    for tool_data in DEFAULT_TOOLS:
        if tool_data["name"] in tools_by_name:
            continue
        tool = Tool(**tool_data)
        session.add(tool)
        created_tools += 1

    session.flush()

    tools_by_name = {tool.name: tool for tool in session.exec(select(Tool))}
    default_tool_names = ["rag_search", "web_search", "calculator"]
    default_tools = [tools_by_name[name] for name in default_tool_names if name in tools_by_name]

    existing_agents = {agent.key: agent for agent in session.exec(select(Agent))}
    for agent_data in DEFAULT_AGENTS:
        if agent_data["key"] in existing_agents:
            continue
        agent = Agent(**agent_data)
        agent.tools = default_tools
        session.add(agent)
        created_agents += 1

    session.commit()
    return created_tools, created_agents
