from fastapi import APIRouter

from app.api.deps import SessionDep
from app.controllers import agent_controller
from app.schemas.agents import AgentCreate, AgentRead, AgentUpdate

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
