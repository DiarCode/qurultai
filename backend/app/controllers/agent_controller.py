from __future__ import annotations

from sqlmodel import Session

from app.schemas.agents import AgentCreate, AgentDocumentsResponse, AgentRead, AgentToolsResponse, AgentUpdate
from app.schemas.knowledge import KnowledgeDocumentRead, KnowledgeDocumentUploadRequest, KnowledgeDocumentUploadResponse
from app.schemas.tools import ToolRead
from app.services import agent_service
from app.services import knowledge_service


def _to_read_model(agent) -> AgentRead:
    data = AgentRead.model_validate(agent).model_dump()
    data["tool_ids"] = [tool.id for tool in agent.tools]
    data["skill_ids"] = [skill.id for skill in agent.skills]
    data["document_ids"] = [doc.id for doc in agent.documents]
    return AgentRead(**data)


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
    return AgentToolsResponse(agent_id=agent_id, tools=[ToolRead.model_validate(tool) for tool in tools])


def add_agent_tool(session: Session, agent_id: str, tool_id: str) -> AgentRead:
    return _to_read_model(agent_service.add_agent_tool(session, agent_id, tool_id))


def remove_agent_tool(session: Session, agent_id: str, tool_id: str) -> AgentRead:
    return _to_read_model(agent_service.remove_agent_tool(session, agent_id, tool_id))


def list_agent_documents(session: Session, agent_id: str) -> AgentDocumentsResponse:
    docs = agent_service.list_agent_documents(session, agent_id)
    items: list[KnowledgeDocumentRead] = []
    for doc in docs:
        data = KnowledgeDocumentRead.model_validate(doc).model_dump()
        data["agent_ids"] = [agent_id]
        items.append(KnowledgeDocumentRead(**data))
    return AgentDocumentsResponse(agent_id=agent_id, documents=items)


def link_document_to_agent(session: Session, agent_id: str, document_id: str) -> AgentDocumentsResponse:
    agent_service.link_document_to_agent(session, agent_id, document_id)
    return list_agent_documents(session, agent_id)


def unlink_document_from_agent(session: Session, agent_id: str, document_id: str) -> AgentDocumentsResponse:
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
    )
    data = KnowledgeDocumentRead.model_validate(doc).model_dump()
    data["agent_ids"] = [agent_id]
    return KnowledgeDocumentUploadResponse(
        document=KnowledgeDocumentRead(**data),
        chunks_ingested=chunks_ingested,
    )
