from fastapi import APIRouter

from app.api.deps import SessionDep
from app.controllers import agent_controller
from app.schemas.agents import AgentCreate, AgentRead, AgentUpdate
from app.schemas.documents import AgentDocumentRequest, DocumentRead
from app.schemas.skills import AgentSkillContentRead, AgentSkillRequest
from app.schemas.tools import AgentToolRead, AgentToolRequest
from app.services import document_service, skill_service, tool_service

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


# --- Agent Documents ---

@router.post("/{agent_id}/documents/attach", response_model=list[str])
def attach_documents(agent_id: str, payload: AgentDocumentRequest, session: SessionDep) -> list[str]:
    agent = document_service.attach_documents_to_agent(session, agent_id, payload.document_ids)
    return [doc.id for doc in agent.documents]


@router.post("/{agent_id}/documents/detach", response_model=list[str])
def detach_documents(agent_id: str, payload: AgentDocumentRequest, session: SessionDep) -> list[str]:
    agent = document_service.detach_documents_from_agent(session, agent_id, payload.document_ids)
    return [doc.id for doc in agent.documents]


@router.get("/{agent_id}/documents", response_model=list[DocumentRead])
def get_agent_documents(agent_id: str, session: SessionDep) -> list[DocumentRead]:
    agent = agent_controller.get_agent(session, agent_id)
    # Re-fetch full agent model for relationships
    from app.services.agent_service import get_agent as get_agent_model
    agent_model = get_agent_model(session, agent_id)
    return [DocumentRead.model_validate(doc) for doc in agent_model.documents]


# --- Agent Skills ---

@router.post("/{agent_id}/skills/attach", response_model=list[str])
def attach_skills(agent_id: str, payload: AgentSkillRequest, session: SessionDep) -> list[str]:
    agent = skill_service.attach_skills_to_agent(session, agent_id, payload.skill_ids)
    return [s.id for s in agent.skills]


@router.post("/{agent_id}/skills/detach", response_model=list[str])
def detach_skills(agent_id: str, payload: AgentSkillRequest, session: SessionDep) -> list[str]:
    agent = skill_service.detach_skills_from_agent(session, agent_id, payload.skill_ids)
    return [s.id for s in agent.skills]


@router.get("/{agent_id}/skills/content", response_model=list[AgentSkillContentRead])
def get_agent_skills_content(agent_id: str, session: SessionDep) -> list[AgentSkillContentRead]:
    items = skill_service.get_agent_skills_content(session, agent_id)
    return [AgentSkillContentRead(**item) for item in items]


# --- Agent Tools ---

@router.post("/{agent_id}/tools/attach", response_model=list[AgentToolRead])
def attach_tools(agent_id: str, payload: AgentToolRequest, session: SessionDep) -> list[AgentToolRead]:
    tool_service.attach_tools_to_agent(session, agent_id, payload.tool_ids, payload.config_overrides)
    items = tool_service.get_agent_tools(session, agent_id)
    return [AgentToolRead(**item) for item in items]


@router.post("/{agent_id}/tools/detach", response_model=list[AgentToolRead])
def detach_tools(agent_id: str, payload: AgentToolRequest, session: SessionDep) -> list[AgentToolRead]:
    tool_service.detach_tools_from_agent(session, agent_id, payload.tool_ids)
    items = tool_service.get_agent_tools(session, agent_id)
    return [AgentToolRead(**item) for item in items]


@router.get("/{agent_id}/tools", response_model=list[AgentToolRead])
def get_agent_tools(agent_id: str, session: SessionDep) -> list[AgentToolRead]:
    items = tool_service.get_agent_tools(session, agent_id)
    return [AgentToolRead(**item) for item in items]
