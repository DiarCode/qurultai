from __future__ import annotations

from sqlmodel import Session, select

from app.core.exceptions import ConflictError, NotFoundError
from app.models.tool import Tool
from app.schemas.tools import ToolCreate, ToolUpdate


def create_tool(session: Session, payload: ToolCreate) -> Tool:
    existing = session.exec(select(Tool).where(Tool.name == payload.name)).first()
    if existing is not None:
        raise ConflictError(f"Tool name '{payload.name}' already exists.")

    tool = Tool(
        name=payload.name,
        description=payload.description,
        input_schema_json=payload.input_schema_json,
        endpoint_url=payload.endpoint_url,
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


def update_tool(session: Session, tool_id: str, payload: ToolUpdate) -> Tool:
    tool = get_tool(session, tool_id)
    updates = payload.model_dump(exclude_unset=True)

    if "name" in updates and updates["name"] != tool.name:
        duplicate = session.exec(select(Tool).where(Tool.name == updates["name"]))
        if duplicate.first() is not None:
            raise ConflictError(f"Tool name '{updates['name']}' already exists.")

    for field_name, value in updates.items():
        setattr(tool, field_name, value)

    session.add(tool)
    session.commit()
    session.refresh(tool)
    return tool


def delete_tool(session: Session, tool_id: str) -> None:
    tool = get_tool(session, tool_id)
    session.delete(tool)
    session.commit()
