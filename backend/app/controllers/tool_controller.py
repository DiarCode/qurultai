from __future__ import annotations

from sqlmodel import Session

from app.schemas.tools import ToolCreate, ToolRead, ToolUpdate
from app.services import tool_service


def create_tool(session: Session, payload: ToolCreate) -> ToolRead:
    return ToolRead.model_validate(tool_service.create_tool(session, payload))


def list_tools(session: Session) -> list[ToolRead]:
    return [ToolRead.model_validate(tool) for tool in tool_service.list_tools(session)]


def get_tool(session: Session, tool_id: str) -> ToolRead:
    return ToolRead.model_validate(tool_service.get_tool(session, tool_id))


def update_tool(session: Session, tool_id: str, payload: ToolUpdate) -> ToolRead:
    return ToolRead.model_validate(tool_service.update_tool(session, tool_id, payload))


def delete_tool(session: Session, tool_id: str) -> None:
    tool_service.delete_tool(session, tool_id)
