from __future__ import annotations

from sqlmodel import Session

from app.schemas.agents import (
    AgentCreate,
    AgentDocumentsResponse,
    AgentRead,
    AgentSkillsResponse,
    AgentToolsResponse,
    AgentUpdate,
)
from app.schemas.knowledge import (
    KnowledgeDocumentRead,
    KnowledgeDocumentUploadRequest,
    KnowledgeDocumentUploadResponse,
)
from app.schemas.skills import SkillRead
from app.schemas.tools import ToolRead
from app.services import agent_service, knowledge_service


def _to_document_read(document, *, agent_id: str | None = None) -> KnowledgeDocumentRead:
    return knowledge_service.build_document_read(document, agent_ids=[agent_id] if agent_id else [])


def _to_read_model(agent) -> AgentRead:
    documents = [
        _to_document_read(document, agent_id=agent.id)
        for document in getattr(agent, "knowledge_documents", []) or []
    ]
    return AgentRead(
        id=agent.id,
        key=agent.key,
        name=agent.name,
        role=agent.role_description,
        description=agent.description,
        system_prompt=agent.system_prompt,
        goals=list(agent.goals_json or []),
        constraints=list(agent.constraints_json or []),
        status=agent.status,
        created_at=agent.created_at,
        updated_at=agent.updated_at,
        tool_ids=[tool.id for tool in agent.tools],
        skill_ids=[skill.id for skill in agent.skills],
        tools=[ToolRead.model_validate(tool) for tool in agent.tools],
        skills=[SkillRead.model_validate(skill) for skill in agent.skills],
        documents=documents,
    )


def create_agent(session: Session, payload: AgentCreate) -> AgentRead:
    return _to_read_model(agent_service.create_agent(session, payload))


def list_agents(session: Session) -> list[AgentRead]:
    return [_to_read_model(agent) for agent in agent_service.list_agents(session)]


def get_agent(session: Session, agent_id: str) -> AgentRead:
    return _to_read_model(agent_service.get_agent(session, agent_id))


def update_agent(session: Session, agent_id: str, payload: AgentUpdate) -> AgentRead:
    return _to_read_model(agent_service.update_agent(session, agent_id, payload))


def delete_agent(session: Session, agent_id: str) -> None:
    agent_service.delete_agent(session, agent_id)


def list_agent_tools(session: Session, agent_id: str) -> AgentToolsResponse:
    tools = agent_service.list_agent_tools(session, agent_id)
    return AgentToolsResponse(
        agent_id=agent_id, tools=[ToolRead.model_validate(tool) for tool in tools]
    )


def add_agent_tool(session: Session, agent_id: str, tool_id: str) -> AgentRead:
    return _to_read_model(agent_service.add_agent_tool(session, agent_id, tool_id))


def remove_agent_tool(session: Session, agent_id: str, tool_id: str) -> AgentRead:
    return _to_read_model(agent_service.remove_agent_tool(session, agent_id, tool_id))


def list_agent_skills(session: Session, agent_id: str) -> AgentSkillsResponse:
    skills = agent_service.list_agent_skills(session, agent_id)
    return AgentSkillsResponse(
        agent_id=agent_id, skills=[SkillRead.model_validate(skill) for skill in skills]
    )


def add_agent_skill(session: Session, agent_id: str, skill_id: str) -> AgentRead:
    return _to_read_model(agent_service.add_agent_skill(session, agent_id, skill_id))


def remove_agent_skill(session: Session, agent_id: str, skill_id: str) -> AgentRead:
    return _to_read_model(agent_service.remove_agent_skill(session, agent_id, skill_id))


def list_agent_documents(session: Session, agent_id: str) -> AgentDocumentsResponse:
    docs = agent_service.list_agent_documents(session, agent_id)
    items = [_to_document_read(doc, agent_id=agent_id) for doc in docs]
    return AgentDocumentsResponse(agent_id=agent_id, documents=items)


def link_document_to_agent(
    session: Session, agent_id: str, document_id: str
) -> AgentDocumentsResponse:
    agent_service.link_document_to_agent(session, agent_id, document_id)
    return list_agent_documents(session, agent_id)


def unlink_document_from_agent(
    session: Session, agent_id: str, document_id: str
) -> AgentDocumentsResponse:
    agent_service.unlink_document_from_agent(session, agent_id, document_id)
    return list_agent_documents(session, agent_id)


def upload_agent_document(
    session: Session,
    agent_id: str,
    payload: KnowledgeDocumentUploadRequest,
) -> KnowledgeDocumentUploadResponse:
    raw_payload = bytes(payload.content_base64) if payload.content_base64 is not None else b""
    if not raw_payload and payload.plain_text is not None:
        raw_payload = payload.plain_text.encode("utf-8")

    doc, chunks_ingested = knowledge_service.upload_document(
        session,
        source_filename=payload.source_filename,
        payload=raw_payload,
        mime_type=payload.mime_type,
        agent_id=agent_id,
        title=payload.title,
        metadata={"source": "agent_upload", "agent_id": agent_id},
    )
    return KnowledgeDocumentUploadResponse(
        document=_to_document_read(doc, agent_id=agent_id),
        chunks_ingested=chunks_ingested,
    )


def upload_agent_document_bytes(
    session: Session,
    agent_id: str,
    *,
    source_filename: str,
    payload: bytes,
    mime_type: str,
    title: str | None = None,
) -> KnowledgeDocumentUploadResponse:
    doc, chunks_ingested = knowledge_service.upload_document(
        session,
        source_filename=source_filename,
        payload=payload,
        mime_type=mime_type,
        agent_id=agent_id,
        title=title,
        metadata={"source": "agent_upload", "agent_id": agent_id},
    )
    return KnowledgeDocumentUploadResponse(
        document=_to_document_read(doc, agent_id=agent_id),
        chunks_ingested=chunks_ingested,
    )
