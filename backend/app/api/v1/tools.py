from fastapi import APIRouter
from fastapi.responses import Response

from app.api.deps import SessionDep
from app.controllers import tool_controller
from app.schemas.tools import ToolCreate, ToolRead, ToolUpdate

router = APIRouter(prefix="/tools", tags=["tools"])


@router.post("", response_model=ToolRead, status_code=201)
def create_tool(payload: ToolCreate, session: SessionDep) -> ToolRead:
    return tool_controller.create_tool(session, payload)


@router.get("", response_model=list[ToolRead])
def list_tools(session: SessionDep) -> list[ToolRead]:
    return tool_controller.list_tools(session)


@router.get("/{tool_id}", response_model=ToolRead)
def get_tool(tool_id: str, session: SessionDep) -> ToolRead:
    return tool_controller.get_tool(session, tool_id)


@router.patch("/{tool_id}", response_model=ToolRead)
def update_tool(tool_id: str, payload: ToolUpdate, session: SessionDep) -> ToolRead:
    return tool_controller.update_tool(session, tool_id, payload)


@router.delete("/{tool_id}", status_code=204)
def delete_tool(tool_id: str, session: SessionDep) -> Response:
    tool_controller.delete_tool(session, tool_id)
    return Response(status_code=204)
