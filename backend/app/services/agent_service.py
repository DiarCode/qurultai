from __future__ import annotations

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.core.exceptions import ConflictError, NotFoundError
from app.models.agent import Agent
from app.models.knowledge_source import KnowledgeSource
from app.models.skill import Skill
from app.models.user import User
from app.schemas.agents import AgentCreate, AgentUpdate
from app.services import audit_service


def _agent_query():
    return select(Agent).options(
        selectinload(Agent.skills),
        selectinload(Agent.knowledge_sources),
    )


def _get_user_if_present(session: Session, user_id: str | None) -> User | None:
    if user_id is None:
        return None
    user = session.get(User, user_id)
    if user is None:
        raise NotFoundError(f"User '{user_id}' was not found.")
    return user


def _get_skills(session: Session, skill_ids: list[str]) -> list[Skill]:
    if not skill_ids:
        return []
    skills = list(session.exec(select(Skill).where(Skill.id.in_(skill_ids))))
    if len(skills) != len(set(skill_ids)):
        raise NotFoundError("One or more skill IDs were not found.")
    return skills


def _get_knowledge_sources(session: Session, knowledge_source_ids: list[str]) -> list[KnowledgeSource]:
    if not knowledge_source_ids:
        return []
    knowledge_sources = list(
        session.exec(select(KnowledgeSource).where(KnowledgeSource.id.in_(knowledge_source_ids)))
    )
    if len(knowledge_sources) != len(set(knowledge_source_ids)):
        raise NotFoundError("One or more knowledge source IDs were not found.")
    return knowledge_sources


def create_agent(session: Session, payload: AgentCreate) -> Agent:
    existing_agent = session.exec(select(Agent).where(Agent.key == payload.key)).first()
    if existing_agent is not None:
        raise ConflictError(f"Agent key '{payload.key}' already exists.")

    _get_user_if_present(session, payload.owner_user_id)
    agent = Agent(
        key=payload.key,
        name=payload.name,
        role=payload.role,
        description=payload.description,
        system_prompt=payload.system_prompt,
        goals_json=payload.goals_json,
        constraints_json=payload.constraints_json,
        output_template=payload.output_template,
        status=payload.status,
        owner_user_id=payload.owner_user_id,
    )
    agent.skills = _get_skills(session, payload.skill_ids)
    agent.knowledge_sources = _get_knowledge_sources(session, payload.knowledge_source_ids)
    session.add(agent)
    audit_service.log_event(
        session,
        entity_type="agent",
        entity_id=agent.id,
        action="created",
        actor_user_id=payload.owner_user_id,
        details_json={"key": payload.key},
    )
    session.commit()
    session.refresh(agent)
    return get_agent(session, agent.id)


def list_agents(session: Session) -> list[Agent]:
    return list(session.exec(_agent_query().order_by(Agent.created_at.desc())))


def get_agent(session: Session, agent_id: str) -> Agent:
    agent = session.exec(_agent_query().where(Agent.id == agent_id)).first()
    if agent is None:
        raise NotFoundError(f"Agent '{agent_id}' was not found.")
    return agent


def update_agent(session: Session, agent_id: str, payload: AgentUpdate) -> Agent:
    agent = get_agent(session, agent_id)
    updates = payload.model_dump(exclude_unset=True)

    if "owner_user_id" in updates:
        _get_user_if_present(session, updates["owner_user_id"])

    skill_ids = updates.pop("skill_ids", None)
    knowledge_source_ids = updates.pop("knowledge_source_ids", None)

    for field_name, value in updates.items():
        setattr(agent, field_name, value)

    if skill_ids is not None:
        agent.skills = _get_skills(session, skill_ids)
    if knowledge_source_ids is not None:
        agent.knowledge_sources = _get_knowledge_sources(session, knowledge_source_ids)

    session.add(agent)
    audit_service.log_event(
        session,
        entity_type="agent",
        entity_id=agent.id,
        action="updated",
        actor_user_id=agent.owner_user_id,
        details_json={"updated_fields": sorted(payload.model_dump(exclude_unset=True).keys())},
    )
    session.commit()
    session.refresh(agent)
    return get_agent(session, agent.id)
