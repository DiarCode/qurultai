from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import Response

from app.api.deps import SessionDep
from app.controllers import agent_controller
from app.schemas.agents import (
    AgentCreate,
    AgentDocumentsResponse,
    AgentRead,
    AgentSkillsResponse,
    AgentToolsResponse,
    AgentUpdate,
)
from app.schemas.knowledge import KnowledgeDocumentUploadRequest, KnowledgeDocumentUploadResponse

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", response_model=AgentRead, status_code=201)
def create_agent(payload: AgentCreate, session: SessionDep) -> AgentRead:
    return agent_controller.create_agent(session, payload)


@router.get("", response_model=list[AgentRead])
def list_agents(session: SessionDep) -> list[AgentRead]:
    return agent_controller.list_agents(session)


@router.get("/{agent_id}", response_model=AgentRead)
def get_agent(agent_id: str, session: SessionDep) -> AgentRead:
    return agent_controller.get_agent(session, agent_id)


@router.patch("/{agent_id}", response_model=AgentRead)
def update_agent(agent_id: str, payload: AgentUpdate, session: SessionDep) -> AgentRead:
    return agent_controller.update_agent(session, agent_id, payload)


@router.delete("/{agent_id}", status_code=204)
def delete_agent(agent_id: str, session: SessionDep) -> Response:
    agent_controller.delete_agent(session, agent_id)
    return Response(status_code=204)


@router.get("/{agent_id}/tools", response_model=AgentToolsResponse)
def list_agent_tools(agent_id: str, session: SessionDep) -> AgentToolsResponse:
    return agent_controller.list_agent_tools(session, agent_id)


@router.post("/{agent_id}/tools/{tool_id}", response_model=AgentRead)
def add_agent_tool(agent_id: str, tool_id: str, session: SessionDep) -> AgentRead:
    return agent_controller.add_agent_tool(session, agent_id, tool_id)


@router.delete("/{agent_id}/tools/{tool_id}", response_model=AgentRead)
def remove_agent_tool(agent_id: str, tool_id: str, session: SessionDep) -> AgentRead:
    return agent_controller.remove_agent_tool(session, agent_id, tool_id)


@router.get("/{agent_id}/skills", response_model=AgentSkillsResponse)
def list_agent_skills(agent_id: str, session: SessionDep) -> AgentSkillsResponse:
    return agent_controller.list_agent_skills(session, agent_id)


@router.post("/{agent_id}/skills/{skill_id}", response_model=AgentRead)
def add_agent_skill(agent_id: str, skill_id: str, session: SessionDep) -> AgentRead:
    return agent_controller.add_agent_skill(session, agent_id, skill_id)


@router.delete("/{agent_id}/skills/{skill_id}", response_model=AgentRead)
def remove_agent_skill(agent_id: str, skill_id: str, session: SessionDep) -> AgentRead:
    return agent_controller.remove_agent_skill(session, agent_id, skill_id)


@router.get("/{agent_id}/documents", response_model=AgentDocumentsResponse)
def list_agent_documents(agent_id: str, session: SessionDep) -> AgentDocumentsResponse:
    return agent_controller.list_agent_documents(session, agent_id)


@router.post(
    "/{agent_id}/documents/upload-file",
    response_model=KnowledgeDocumentUploadResponse,
    status_code=201,
)
async def upload_agent_document_file(
    agent_id: str,
    session: SessionDep,
    file: UploadFile = File(...),
    title: str | None = Form(None),
) -> KnowledgeDocumentUploadResponse:
    payload = await file.read()
    return agent_controller.upload_agent_document_bytes(
        session,
        agent_id,
        source_filename=file.filename or "upload.bin",
        payload=payload,
        mime_type=file.content_type or "application/octet-stream",
        title=title,
    )


@router.post(
    "/{agent_id}/documents/upload", response_model=KnowledgeDocumentUploadResponse, status_code=201
)
def upload_agent_document(
    agent_id: str,
    payload: KnowledgeDocumentUploadRequest,
    session: SessionDep,
) -> KnowledgeDocumentUploadResponse:
    return agent_controller.upload_agent_document(session, agent_id, payload)


@router.post("/{agent_id}/documents/{document_id}", response_model=AgentDocumentsResponse)
def link_agent_document(
    agent_id: str, document_id: str, session: SessionDep
) -> AgentDocumentsResponse:
    return agent_controller.link_document_to_agent(session, agent_id, document_id)


@router.delete("/{agent_id}/documents/{document_id}", response_model=AgentDocumentsResponse)
def unlink_agent_document(
    agent_id: str, document_id: str, session: SessionDep
) -> AgentDocumentsResponse:
    return agent_controller.unlink_document_from_agent(session, agent_id, document_id)
