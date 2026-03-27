from fastapi import APIRouter

from app.api.deps import SessionDep
from app.schemas.tools import (
    BuiltinToolDefinition,
    ToolCreate,
    ToolExecuteRequest,
    ToolExecuteResponse,
    ToolRead,
    ToolUpdate,
)
from app.services import tool_service
from app.services.tool_registry import execute_builtin_tool, get_builtin_tool_definitions

router = APIRouter(prefix="/tools", tags=["tools"])


@router.post("", response_model=ToolRead, status_code=201)
def create_tool(payload: ToolCreate, session: SessionDep) -> ToolRead:
    tool = tool_service.create_tool(
        session,
        name=payload.name,
        description=payload.description,
        tool_type=payload.tool_type,
        input_schema_json=payload.input_schema_json,
        output_schema_json=payload.output_schema_json,
        configuration_json=payload.configuration_json,
        endpoint_url=payload.endpoint_url,
    )
    return ToolRead.model_validate(tool)


@router.get("", response_model=list[ToolRead])
def list_tools(session: SessionDep) -> list[ToolRead]:
    return [ToolRead.model_validate(t) for t in tool_service.list_tools(session)]


@router.get("/builtins", response_model=list[BuiltinToolDefinition])
def list_builtin_tools() -> list[BuiltinToolDefinition]:
    return [BuiltinToolDefinition(**defn) for defn in get_builtin_tool_definitions()]


@router.get("/{tool_id}", response_model=ToolRead)
def get_tool(tool_id: str, session: SessionDep) -> ToolRead:
    return ToolRead.model_validate(tool_service.get_tool(session, tool_id))


@router.patch("/{tool_id}", response_model=ToolRead)
def update_tool(tool_id: str, payload: ToolUpdate, session: SessionDep) -> ToolRead:
    updates = payload.model_dump(exclude_unset=True)
    tool = tool_service.update_tool(session, tool_id, **updates)
    return ToolRead.model_validate(tool)


@router.delete("/{tool_id}", status_code=204)
def delete_tool(tool_id: str, session: SessionDep) -> None:
    tool_service.delete_tool(session, tool_id)


@router.post("/execute", response_model=ToolExecuteResponse)
def execute_tool(payload: ToolExecuteRequest) -> ToolExecuteResponse:
    result = execute_builtin_tool(payload.tool_name, payload.params)
    return ToolExecuteResponse(tool_name=payload.tool_name, result=result)
