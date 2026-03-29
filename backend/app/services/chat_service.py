from __future__ import annotations

import html
import re
from collections.abc import Callable, Iterable
from typing import Any

from sqlmodel import Session, func, select

from app.core.config import get_settings
from app.core.exceptions import NotFoundError
from app.core.utils import utc_now
from app.db.session import SessionLocal
from app.models.agent import Agent
from app.models.chat_message import ChatMessage
from app.models.chat_run import ChatRun
from app.models.chat_run_event import ChatRunEvent
from app.models.knowledge_document import KnowledgeDocument
from app.models.room import Room
from app.models.room_event import RoomDocumentLink
from app.schemas.chat import (
    ChatMessageRead,
    ChatModePreference,
    ChatParticipantRead,
    ChatRunEventRead,
    ChatRunRead,
    ChatSessionRead,
    ChatSessionSummaryRead,
    CitationRead,
    MessageActionRead,
    MessageAttachmentRead,
    UploadedDocumentRead,
)
from app.schemas.structured_outputs import (
    FinalAnswerPayload,
    RoutingDecision,
    SpecialistAnalysis,
)
from app.services import knowledge_service, llm_service, report_service

ASSISTANT_SYSTEM_PROMPT = """
You are Qurultai, a polished policy and research assistant inside a persistent chat workspace.
Answer like one smart lead analyst, not a committee template.
Use evidence when available, say what is uncertain, avoid repetition, and keep the tone natural.
Do not invent citations or claim certainty beyond the provided material.
""".strip()

SPECIALIST_PROMPT = """
You are a specialist contributing to a final user-facing answer.
Give a concise analysis focused on your domain, with explicit risks, practical recommendation, and where the evidence is thin.
Stay grounded in the provided evidence and conversation.
""".strip()

MODE_AGENT_LIMITS: dict[str, int] = {
    "direct_answer": 0,
    "rag_answer": 1,
    "specialist_assist": 2,
    "council": 4,
}


def _session_or_404(session: Session, session_id: str) -> Room:
    room = session.get(Room, session_id)
    if room is None:
        raise NotFoundError(f"Session '{session_id}' was not found.")
    return room


def _run_or_404(session: Session, run_id: str) -> ChatRun:
    run = session.get(ChatRun, run_id)
    if run is None:
        raise NotFoundError(f"Run '{run_id}' was not found.")
    return run


def _message_or_404(session: Session, message_id: str) -> ChatMessage:
    message = session.get(ChatMessage, message_id)
    if message is None:
        raise NotFoundError(f"Message '{message_id}' was not found.")
    return message


def _truncate(text: str | None, limit: int = 180) -> str | None:
    if not text:
        return None
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return f"{compact[: limit - 1].rstrip()}…"


def _slug_title(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return "New chat"
    words = cleaned.split(" ")
    title = " ".join(words[:8]).strip(" .,:;")
    return title[:80] or "New chat"


def _download_url(document_id: str) -> str:
    return f"/api/v1/files/{document_id}/download"


def _report_download_url(run_id: str, format_name: str) -> str:
    return f"/api/v1/chat/runs/{run_id}/report/download?format={format_name}"


def _safe_llm(
    *,
    prompt: str,
    fallback: str,
    system_prompt: str | None = None,
    context: str | None = None,
    skills_content: list[str] | None = None,
    max_output_tokens: int | None = None,
) -> str:
    try:
        result = llm_service.invoke_llm_with_context(
            prompt=prompt,
            system_prompt=system_prompt,
            context=context,
            skills_content=skills_content,
            max_output_tokens=max_output_tokens,
        )
        return result.strip() or fallback
    except Exception:
        return fallback


def _next_event_sequence(session: Session, run_id: str) -> int:
    current = session.exec(
        select(func.max(ChatRunEvent.sequence)).where(ChatRunEvent.run_id == run_id)
    ).one()
    return int(current or 0) + 1


def append_run_event(
    session: Session,
    run_id: str,
    event_type: str,
    payload: dict[str, Any],
) -> ChatRunEvent:
    event = ChatRunEvent(
        run_id=run_id,
        sequence=_next_event_sequence(session, run_id),
        event_type=event_type,
        payload_json=payload,
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def list_run_events(session: Session, run_id: str, after_sequence: int = 0) -> list[ChatRunEvent]:
    _run_or_404(session, run_id)
    return list(
        session.exec(
            select(ChatRunEvent)
            .where(ChatRunEvent.run_id == run_id, ChatRunEvent.sequence > after_sequence)
            .order_by(ChatRunEvent.sequence.asc())
        )
    )


def _message_attachment_from_document(document: KnowledgeDocument) -> MessageAttachmentRead:
    return MessageAttachmentRead(
        id=document.id,
        name=document.title or document.source_filename,
        mime_type=document.mime_type,
        size_bytes=document.size_bytes,
        download_url=_download_url(document.id),
        created_at=document.created_at,
    )


def _uploaded_document_read(document: KnowledgeDocument, session_id: str) -> UploadedDocumentRead:
    metadata = document.metadata_json or {}
    return UploadedDocumentRead(
        id=document.id,
        session_id=session_id,
        name=document.title or document.source_filename,
        mime_type=document.mime_type,
        size_bytes=document.size_bytes,
        storage_path=document.s3_key,
        download_url=_download_url(document.id),
        linked_run_id=str(metadata.get("run_id")) if metadata.get("run_id") else None,
        created_at=document.created_at,
    )


def _citation_from_document(
    document: KnowledgeDocument,
    *,
    snippet: str | None,
    score: float | None,
    location: str | None = None,
) -> CitationRead:
    return CitationRead(
        id=f"citation-{document.id}-{abs(hash((snippet or '', location or ''))) % 100000}",
        document_id=document.id,
        title=document.title or document.source_filename,
        snippet=_truncate(snippet, limit=280),
        score=score,
        location=location,
        download_url=_download_url(document.id),
    )


def _participant_from_agent(agent: Agent, *, reason: str | None = None) -> ChatParticipantRead:
    return ChatParticipantRead(
        id=agent.id,
        key=agent.key,
        name=agent.name,
        role=agent.role_description,
        status=agent.status,
        reason=reason,
    )


def _message_read(message: ChatMessage) -> ChatMessageRead:
    return ChatMessageRead(
        id=message.id,
        session_id=message.session_id,
        run_id=message.run_id,
        role=message.role,
        type=message.message_type,
        source_agent_id=message.source_agent_id,
        source_agent_name=message.source_agent_name,
        content=message.content,
        html_content=message.html_content,
        citations=[CitationRead.model_validate(item) for item in message.citations_json or []],
        attachments=[
            MessageAttachmentRead.model_validate(item) for item in message.attachments_json or []
        ],
        actions=[MessageActionRead.model_validate(item) for item in message.actions_json or []],
        metadata=dict(message.metadata_json or {}),
        status=message.status,
        created_at=message.created_at,
    )


def _summary_read(room: Room) -> ChatSessionSummaryRead:
    return ChatSessionSummaryRead(
        id=room.id,
        title=room.title,
        created_at=room.created_at,
        updated_at=room.updated_at,
        status=room.status,
        last_message_preview=room.last_message_preview,
    )


def _event_read(event: ChatRunEvent) -> ChatRunEventRead:
    return ChatRunEventRead(
        id=event.id,
        run_id=event.run_id,
        sequence=event.sequence,
        event_type=event.event_type,
        created_at=event.created_at,
        payload=event.payload_json,
    )


def _run_read(session: Session, run: ChatRun, *, include_events: bool = True) -> ChatRunRead:
    events = list_run_events(session, run.id) if include_events else []
    return ChatRunRead(
        id=run.id,
        session_id=run.session_id,
        input_message_id=run.input_message_id,
        output_message_id=run.output_message_id,
        mode=run.mode,  # type: ignore[arg-type]
        selected_agents=[
            ChatParticipantRead.model_validate(item) for item in run.selected_agents_json or []
        ],
        status=run.status,  # type: ignore[arg-type]
        started_at=run.started_at,
        finished_at=run.finished_at,
        events=[_event_read(event) for event in events],
    )


def _session_documents(session: Session, session_id: str) -> list[KnowledgeDocument]:
    links = list(
        session.exec(select(RoomDocumentLink).where(RoomDocumentLink.room_id == session_id))
    )
    if not links:
        return []
    document_ids = [link.document_id for link in links]
    return list(
        session.exec(
            select(KnowledgeDocument)
            .where(KnowledgeDocument.id.in_(document_ids))
            .order_by(KnowledgeDocument.created_at.asc())
        )
    )


def build_session_read(session: Session, session_id: str) -> ChatSessionRead:
    room = _session_or_404(session, session_id)
    messages = list(
        session.exec(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
    )
    runs = list(
        session.exec(
            select(ChatRun)
            .where(ChatRun.session_id == session_id)
            .order_by(ChatRun.created_at.asc())
        )
    )
    documents = _session_documents(session, session_id)
    return ChatSessionRead(
        **_summary_read(room).model_dump(),
        messages=[_message_read(message) for message in messages],
        documents=[_uploaded_document_read(document, session_id) for document in documents],
        runs=[_run_read(session, run) for run in runs],
    )


def create_session(session: Session, title: str | None = None) -> Room:
    room = Room(
        title=(title or "New chat").strip() or "New chat", status="active", initial_query=""
    )
    session.add(room)
    session.commit()
    session.refresh(room)
    return room


def list_sessions(session: Session) -> list[Room]:
    return list(session.exec(select(Room).order_by(Room.updated_at.desc())))


def get_session_read(session: Session, session_id: str) -> ChatSessionRead:
    return build_session_read(session, session_id)


def _recent_conversation(messages: Iterable[ChatMessage], *, limit: int = 10) -> str:
    recent = list(messages)[-limit:]
    rendered: list[str] = []
    for message in recent:
        if not message.content.strip():
            continue
        speaker = message.source_agent_name or message.role.title()
        rendered.append(f"{speaker}: {message.content.strip()}")
    return "\n".join(rendered)


def _active_agents(session: Session) -> list[Agent]:
    return list(
        session.exec(
            select(Agent)
            .where(Agent.status.in_(["active", "draft", "ACTIVE", "DRAFT"]))
            .order_by(Agent.created_at.asc())
        )
    )


def _score_agent(agent: Agent, text: str) -> int:
    haystack = " ".join(
        [
            agent.name,
            agent.key,
            agent.role_description,
            agent.description or "",
            agent.system_prompt,
            " ".join(agent.goals_json or []),
            " ".join(agent.constraints_json or []),
            " ".join(skill.name for skill in agent.skills),
            " ".join(skill.description or "" for skill in agent.skills),
        ]
    ).lower()
    tokens = {
        token for token in re.findall(r"[a-zA-Zа-яА-Я0-9_-]{4,}", text.lower()) if len(token) >= 4
    }
    return sum(2 if token in haystack else 0 for token in tokens)


def _default_selected_agents(
    *,
    mode: str,
    matched_agents: list[tuple[int, Agent]],
    active_agents: list[Agent],
    reason: str,
) -> list[ChatParticipantRead]:
    limit = MODE_AGENT_LIMITS.get(mode, 0)
    if limit <= 0:
        return []

    ranked = [agent for _score, agent in matched_agents[:limit]]
    if len(ranked) < limit:
        seen_ids = {agent.id for agent in ranked}
        ranked.extend(agent for agent in active_agents if agent.id not in seen_ids)

    return [_participant_from_agent(agent, reason=reason) for agent in ranked[:limit]]


def _request_signals(content: str, *, docs_present: bool) -> dict[str, Any]:
    lowered = content.lower()
    numbers = [int(match) for match in re.findall(r"\b\d+\b", lowered)]
    large_numeric_scale = max(numbers) if numbers else 0

    multisided_phrases = [
        "с разных сторон",
        "разные стороны",
        "всесторон",
        "комплексно",
        "насколько это сложно",
        "по направлениям",
        "по аспектам",
    ]
    public_sector_terms = [
        "школ",
        "больниц",
        "дорог",
        "министер",
        "парламент",
        "госпрограм",
        "государств",
        "акимат",
        "республика казахстан",
        "казахстан",
    ]
    infrastructure_terms = [
        "стро",
        "инфраструкт",
        "подряд",
        "объект",
        "смет",
        "проект",
        "школ",
        "больниц",
        "энерг",
        "транспорт",
        "вода",
        "иррига",
    ]
    high_risk_terms = [
        "бюджет",
        "финанс",
        "закон",
        "регуля",
        "лиценз",
        "эколог",
        "безопас",
        "риски",
        "госзакуп",
        "разрешен",
    ]

    return {
        "docs_present": docs_present,
        "word_count": len(re.findall(r"\S+", content)),
        "question_count": content.count("?"),
        "mentions_multisided_analysis": any(phrase in lowered for phrase in multisided_phrases),
        "mentions_public_sector": any(term in lowered for term in public_sector_terms),
        "mentions_infrastructure": any(term in lowered for term in infrastructure_terms),
        "mentions_high_risk_constraints": any(term in lowered for term in high_risk_terms),
        "large_numeric_scale": large_numeric_scale,
        "looks_like_large_program": large_numeric_scale >= 10
        or (
            "сто" in lowered
            and any(term in lowered for term in ["школ", "больниц", "дом", "объект"])
        ),
    }


def _classify_request(
    session: Session,
    room: Room,
    content: str,
    new_documents: list[KnowledgeDocument],
    mode_preference: ChatModePreference = "auto",
) -> tuple[str, list[ChatParticipantRead], dict[str, Any]]:
    lowered = content.lower()
    words = re.findall(r"\S+", content)
    docs_present = bool(new_documents or _session_documents(session, room.id))
    request_signals = _request_signals(content, docs_present=docs_present)

    cross_domain_triggers = [
        "trade-off",
        "tradeoff",
        "compare",
        "matrix",
        "между",
        "риски",
        "strategy",
        "стратег",
        "roadmap",
        "scenario",
        "сценар",
        "conflict",
        "противореч",
        "cross-domain",
    ]
    high_risk_triggers = [
        "legal",
        "compliance",
        "budget",
        "procurement",
        "регуля",
        "закон",
        "бюджет",
        "финанс",
        "лиценз",
        "эколог",
    ]

    complexity = 0
    if len(words) > 18:
        complexity += 1
    if len(words) > 40:
        complexity += 1
    if docs_present:
        complexity += 1
    if any(trigger in lowered for trigger in cross_domain_triggers):
        complexity += 2
    if any(trigger in lowered for trigger in high_risk_triggers):
        complexity += 1
    if content.count("?") > 1 or content.count("\n") >= 2:
        complexity += 1
    if request_signals["mentions_multisided_analysis"]:
        complexity += 2
    if request_signals["mentions_infrastructure"]:
        complexity += 1
    if request_signals["looks_like_large_program"]:
        complexity += 2
    if request_signals["mentions_public_sector"]:
        complexity += 1

    ranked_agents = sorted(
        ((_score_agent(agent, content), agent) for agent in _active_agents(session)),
        key=lambda item: item[0],
        reverse=True,
    )
    matched_agents = [(score, agent) for score, agent in ranked_agents if score > 0]

    active_agents = _active_agents(session)
    if complexity <= 1 and not docs_present:
        mode = "direct_answer"
        selected: list[ChatParticipantRead] = []
    elif docs_present and complexity <= 2 and len(matched_agents) <= 1:
        mode = "rag_answer"
        selected = (
            [_participant_from_agent(matched_agents[0][1], reason="document-grounded answer")]
            if matched_agents
            else []
        )
    elif complexity >= 4 or (len(matched_agents) >= 2 and complexity >= 2):
        mode = "council"
        selected = [
            _participant_from_agent(agent, reason="cross-domain or higher-risk question")
            for _score, agent in matched_agents[:3]
        ]
    else:
        mode = "specialist_assist"
        selected = [
            _participant_from_agent(agent, reason="targeted domain expertise")
            for _score, agent in matched_agents[:2]
        ]

    diagnostics = {
        "complexity_score": complexity,
        "docs_present": docs_present,
        "matched_agent_count": len(matched_agents),
        "request_signals": request_signals,
        "mode_preference": mode_preference,
    }
    if mode_preference != "auto":
        mode = mode_preference
        selected = _default_selected_agents(
            mode=mode,
            matched_agents=matched_agents,
            active_agents=active_agents,
            reason="user-selected mode",
        )
        diagnostics["mode_locked_by_user"] = True

    settings = get_settings()
    if (
        settings.ENABLE_LLM_CALLS
        and settings.LLM_PROVIDER.lower() == "openai"
        and settings.OPENAI_API_KEY
    ):
        fallback_decision = RoutingDecision(
            mode=mode_preference if mode_preference != "auto" else mode,
            complexity_level=(
                "high_risk"
                if (mode_preference if mode_preference != "auto" else mode) == "council"
                else "complex"
                if (mode_preference if mode_preference != "auto" else mode) == "specialist_assist"
                else "moderate"
                if (mode_preference if mode_preference != "auto" else mode) == "rag_answer"
                else "simple"
            ),
            rationale=(
                "User-selected mode"
                if mode_preference != "auto"
                else "Heuristic fallback"
            ),
            should_use_retrieval=docs_present
            or (mode_preference == "rag_answer"),
            delegation_reasons=[],
            selected_agent_keys=[participant.key for participant in selected],
        )
        agent_cards = [
            {
                "key": agent.key,
                "name": agent.name,
                "role": agent.role_description,
                "description": agent.description or "",
                "skills": [skill.key for skill in agent.skills],
            }
            for agent in active_agents
        ]
        mode_instruction = (
            "The user explicitly selected the mode below. Keep `mode` fixed to that exact value and only decide which agents, if any, should support it.\n"
            f"Forced mode: {mode_preference}\n"
            "For direct_answer select zero agents. For rag_answer select at most one agent. "
            "For specialist_assist select one or two agents. For council select three or four agents.\n\n"
            if mode_preference != "auto"
            else
            "Classify the request into exactly one mode: direct_answer, rag_answer, specialist_assist, or council.\n"
            "Choose council for large-scale, cross-ministerial, cross-branch, multi-stakeholder, or politically risky tasks. "
            "Choose specialist_assist for narrower but still expert-heavy tasks. "
            "Choose direct_answer only for prompts that one strong assistant can answer cleanly without visible orchestration.\n\n"
            "When the user asks for analysis from different sides, for a large rollout, or for a nationwide public build/program, "
            "do not choose direct_answer.\n"
            "For council choose 3-4 agents. For specialist_assist choose 1-2 agents. For direct_answer choose zero agents.\n\n"
        )
        decision = _safe_structured_llm(
            prompt=(
                f"{mode_instruction}"
                f"Question:\n{content}\n\n"
                f"Has session documents: {docs_present}\n"
                f"Available institutional agents: {agent_cards}\n"
                f"Request signals: {request_signals}\n"
                f"Heuristic diagnostics: {diagnostics}"
            ),
            response_model=RoutingDecision,
            fallback=fallback_decision,
            system_prompt=(
                "You are Qurultai's routing layer. Prefer the simplest mode that still gives a grounded, useful answer. "
                "The available agents represent Kazakhstan government institutions, ministries, and parliamentary committees. "
                "Select the institutions that would materially shape the answer, not generic experts. "
                "Do not send simple prompts to a council, but do escalate large public programs, capital builds, multi-ministry delivery, "
                "or prompts explicitly asking for analysis from different sides. "
                "If the question resembles building many schools, hospitals, roads, utilities, or another national rollout, it is not direct. "
                "If the user explicitly selected a mode, obey that mode and optimize agent choice within it."
            ),
            max_output_tokens=settings.OPENAI_MAX_OUTPUT_TOKENS_ROUTING,
        )
        if mode_preference != "auto":
            decision.mode = mode_preference
        selected_keys = [
            key
            for key in decision.selected_agent_keys
            if key in {agent.key for agent in active_agents}
        ]
        if decision.mode == "direct_answer":
            selected_keys = []
        elif decision.mode == "rag_answer":
            selected_keys = selected_keys[:1]
        elif decision.mode == "specialist_assist":
            selected_keys = selected_keys[:2]
        else:
            selected_keys = selected_keys[:4]

        if not selected_keys and decision.mode != "direct_answer":
            fallback_count = MODE_AGENT_LIMITS.get(decision.mode, 0)
            selected_keys = [agent.key for _score, agent in matched_agents[:fallback_count]]
            if len(selected_keys) < fallback_count:
                seen_keys = set(selected_keys)
                selected_keys.extend(
                    agent.key for agent in active_agents if agent.key not in seen_keys
                )
            selected_keys = selected_keys[:fallback_count]

        active_agent_map = {agent.key: agent for agent in active_agents}
        selected = [
            _participant_from_agent(active_agent_map[key], reason=decision.rationale)
            for key in selected_keys
            if key in active_agent_map
        ]
        mode = decision.mode
        diagnostics["routing_rationale"] = decision.rationale
        diagnostics["routing_complexity_level"] = decision.complexity_level
        diagnostics["routing_delegation_reasons"] = decision.delegation_reasons
        diagnostics["structured_routing"] = True

    return mode, selected, diagnostics


def _safe_structured_llm(
    *,
    prompt: str,
    response_model: type[Any],
    fallback: Any,
    system_prompt: str | None = None,
    context: str | None = None,
    skills_content: list[str] | None = None,
    max_output_tokens: int | None = None,
) -> Any:
    try:
        return llm_service.invoke_structured(
            prompt=prompt,
            response_model=response_model,
            system_prompt=system_prompt,
            context=context,
            skills_content=skills_content,
            max_output_tokens=max_output_tokens,
        )
    except Exception:
        return fallback


def _mode_output_budget(
    *,
    mode: str,
    question: str,
    docs_present: bool,
    participant_count: int = 0,
) -> int:
    settings = get_settings()
    base = {
        "direct_answer": settings.OPENAI_MAX_OUTPUT_TOKENS_DIRECT,
        "rag_answer": settings.OPENAI_MAX_OUTPUT_TOKENS_RAG,
        "specialist_assist": settings.OPENAI_MAX_OUTPUT_TOKENS_SPECIALIST,
        "council": settings.OPENAI_MAX_OUTPUT_TOKENS_COUNCIL,
    }.get(mode, settings.OPENAI_MAX_OUTPUT_TOKENS_DIRECT)

    word_count = len(re.findall(r"\S+", question))
    bonus = min(220, word_count * 4)
    if docs_present:
        bonus += 90
    bonus += min(180, participant_count * 45)

    ceiling = {
        "direct_answer": settings.OPENAI_MAX_OUTPUT_TOKENS_DIRECT + 80,
        "rag_answer": settings.OPENAI_MAX_OUTPUT_TOKENS_RAG + 120,
        "specialist_assist": settings.OPENAI_MAX_OUTPUT_TOKENS_SPECIALIST + 140,
        "council": settings.OPENAI_MAX_OUTPUT_TOKENS_COUNCIL + 180,
    }.get(mode, settings.OPENAI_MAX_OUTPUT_TOKENS_DIRECT + 80)
    return min(base + bonus, ceiling)


def _specialist_message_budget(question: str) -> int:
    settings = get_settings()
    return min(
        settings.OPENAI_MAX_OUTPUT_TOKENS_SPECIALIST_MESSAGE + len(re.findall(r"\S+", question)) * 2,
        settings.OPENAI_MAX_OUTPUT_TOKENS_SPECIALIST_MESSAGE + 120,
    )


def _chunk_text(text: str, *, size: int = 120) -> list[str]:
    if not text:
        return []
    return [text[index : index + size] for index in range(0, len(text), size)]


def _tool_call_payload(
    *,
    name: str,
    status: str,
    input_payload: dict[str, Any],
    output_summary: str | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "input": input_payload,
        "output_summary": output_summary,
    }


def _analysis_to_note(analysis: SpecialistAnalysis) -> str:
    fragments = [analysis.summary]
    if analysis.key_findings:
        fragments.append("Key findings: " + "; ".join(analysis.key_findings))
    if analysis.risks:
        fragments.append("Risks: " + "; ".join(analysis.risks))
    fragments.append("Recommendation: " + analysis.recommendation)
    return " ".join(fragment.strip() for fragment in fragments if fragment.strip())


def _analysis_to_markdown(analysis: SpecialistAnalysis) -> str:
    sections = ["## Position", analysis.summary.strip()]
    if analysis.key_findings:
        sections.extend(["", "## Key findings", *[f"- {item}" for item in analysis.key_findings]])
    if analysis.risks:
        sections.extend(["", "## Risks", *[f"- {item}" for item in analysis.risks]])
    sections.extend(["", "## Recommendation", analysis.recommendation.strip()])
    return "\n".join(section for section in sections if section is not None).strip()


def _debate_message_payload(
    *,
    run_id: str,
    role: str,
    source_agent_id: str | None,
    source_agent_name: str | None,
    stage: str,
    content: str,
    citations: list[CitationRead] | None = None,
    tool_calls: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "id": f"{role}-{abs(hash((run_id, source_agent_id, stage, content[:48]))) % 1000000}",
        "run_id": run_id,
        "role": role,
        "source_agent_id": source_agent_id,
        "source_agent_name": source_agent_name,
        "stage": stage,
        "status": "completed",
        "content": content,
        "citations": [citation.model_dump(mode="json") for citation in citations or []],
        "tool_calls": tool_calls or [],
        "is_partial": False,
        "created_at": utc_now().isoformat(),
    }


def _emit_debate_message_stream(session: Session, *, run_id: str, message: dict[str, Any]) -> None:
    content = str(message.get("content") or "")
    for chunk in _chunk_text(content):
        append_run_event(
            session,
            run_id,
            "agent_message_delta",
            {
                "message_id": message["id"],
                "role": message["role"],
                "source_agent_id": message.get("source_agent_id"),
                "source_agent_name": message.get("source_agent_name"),
                "stage": message.get("stage"),
                "delta": chunk,
            },
        )
    append_run_event(session, run_id, "agent_message_final", {"message": message})


def _dedupe_citations(citations: list[CitationRead]) -> list[CitationRead]:
    deduped: dict[tuple[str | None, str | None, str | None], CitationRead] = {}
    for citation in citations:
        key = (
            citation.document_id,
            (citation.location or "").strip().lower() or None,
            (citation.snippet or "").strip().lower()[:120] or None,
        )
        current = deduped.get(key)
        if current is None or (citation.score or 0.0) > (current.score or 0.0):
            deduped[key] = citation
    return list(deduped.values())


def _session_citations(
    session: Session,
    room: Room,
    query: str,
    *,
    limit: int = 6,
) -> list[CitationRead]:
    documents = _session_documents(session, room.id)
    if not documents:
        return []

    hits = knowledge_service.search_documents(
        session, query=query, limit=max(limit * 3, 8), agent_id=None
    )
    document_map = {document.id: document for document in documents}

    citations: list[CitationRead] = []
    for hit in hits:
        document_id = str(hit.get("document_id") or "")
        document = document_map.get(document_id)
        if document is None:
            continue
        citations.append(
            _citation_from_document(
                document,
                snippet=str(hit.get("text") or "") or document.text_preview,
                score=float(hit.get("score") or 0.0),
                location=str(hit.get("location") or "") or None,
            )
        )

    if not citations:
        for document in documents[:limit]:
            citations.append(
                _citation_from_document(
                    document,
                    snippet=document.text_preview,
                    score=None,
                    location="Document preview",
                )
            )

    citations.sort(key=lambda item: float(item.score or 0.0), reverse=True)
    return _dedupe_citations(citations)[:limit]


def _render_message_html(
    *,
    answer_payload: FinalAnswerPayload,
    citations: list[CitationRead],
    participants: list[ChatParticipantRead],
    confidence: str,
    uncertainty: str | None,
    mode: str,
    analysis_html: str | None = None,
) -> str:
    answer_html = report_service.render_markdown_html(answer_payload.answer_markdown)
    participant_html = ""
    if participants:
        participant_html = (
            '<div class="q-participants">'
            + "".join(
                f'<span class="q-chip">{html.escape(item.name)}</span>' for item in participants
            )
            + "</div>"
        )

    citations_html = ""
    if citations:
        citations_html = (
            '<div class="q-sources"><h4>Sources</h4><ul>'
            + "".join(
                "<li>"
                f"<strong>{html.escape(citation.title)}</strong>"
                + (f"<span> · {html.escape(citation.location)}</span>" if citation.location else "")
                + (f"<p>{html.escape(citation.snippet)}</p>" if citation.snippet else "")
                + "</li>"
                for citation in citations[:5]
            )
            + "</ul></div>"
        )

    analysis_block = (
        f'<details class="q-analysis"><summary>Expanded analysis</summary>{analysis_html}</details>'
        if analysis_html
        else ""
    )
    uncertainty_block = (
        f'<div class="q-note"><strong>Watchouts:</strong> {html.escape(uncertainty)}</div>'
        if uncertainty
        else ""
    )
    key_points_block = ""
    if answer_payload.key_points:
        key_points_block = (
            '<section class="q-section-card"><h4>Key points</h4><ul class="q-list">'
            + "".join(f"<li>{html.escape(point)}</li>" for point in answer_payload.key_points)
            + "</ul></section>"
        )
    risks_block = ""
    if answer_payload.risks:
        risks_block = (
            '<section class="q-section-card q-section-card--warning"><h4>Risks and watchouts</h4><ul class="q-list">'
            + "".join(f"<li>{html.escape(item)}</li>" for item in answer_payload.risks)
            + "</ul></section>"
        )
    recommendations_block = ""
    if answer_payload.recommendations:
        recommendations_block = (
            '<section class="q-section-card"><h4>Recommended actions</h4><ol class="q-list q-list--ordered">'
            + "".join(f"<li>{html.escape(item)}</li>" for item in answer_payload.recommendations)
            + "</ol></section>"
        )
    next_steps_block = ""
    if answer_payload.suggested_next_steps:
        next_steps_block = (
            '<section class="q-section-card"><h4>Next steps</h4><ol class="q-list q-list--ordered">'
            + "".join(
                f"<li>{html.escape(item)}</li>" for item in answer_payload.suggested_next_steps
            )
            + "</ol></section>"
        )

    return f"""
    <article class="q-answer-card" data-mode="{html.escape(mode)}">
      <div class="q-meta">
        <span class="q-pill">{html.escape(mode.replace("_", " "))}</span>
        <span class="q-pill q-pill--soft">Confidence: {html.escape(confidence)}</span>
      </div>
      <div class="q-summary">{html.escape(answer_payload.summary)}</div>
      {participant_html}
      <div class="q-answer-body q-prose">{answer_html}</div>
      {key_points_block}
      {risks_block}
      {recommendations_block}
      {next_steps_block}
      {uncertainty_block}
      {citations_html}
      {analysis_block}
    </article>
    """.strip()


def _report_markdown(
    *,
    question: str,
    answer_payload: FinalAnswerPayload,
    citations: list[CitationRead],
    participants: list[ChatParticipantRead],
    mode: str,
    confidence: str,
    uncertainty: str | None,
) -> str:
    lines = [
        f"# {answer_payload.report_title}",
        "",
        "> Professional brief generated by Qurultai",
        "",
        "## Executive Summary",
        answer_payload.summary.strip(),
        "",
        "## User Request",
        question.strip(),
        "",
        "## Core Answer",
        answer_payload.answer_markdown.strip(),
        "",
        "## Delivery Context",
        f"- Mode: {mode.replace('_', ' ')}",
        f"- Confidence: {confidence}",
        "",
    ]
    if answer_payload.key_points:
        lines.extend(["## Key Points"])
        lines.extend(f"- {item}" for item in answer_payload.key_points)
        lines.append("")
    if answer_payload.risks:
        lines.extend(["## Risks and Watchouts"])
        lines.extend(f"- {item}" for item in answer_payload.risks)
        lines.append("")
    if answer_payload.recommendations:
        lines.extend(["## Recommended Actions"])
        lines.extend(f"1. {item}" for item in answer_payload.recommendations)
        lines.append("")
    if answer_payload.suggested_next_steps:
        lines.extend(["## Immediate Next Steps"])
        lines.extend(f"1. {item}" for item in answer_payload.suggested_next_steps)
        lines.append("")
    if participants:
        lines.extend(["## Participating Specialists"])
        lines.extend(f"- {participant.name}: {participant.role}" for participant in participants)
        lines.append("")
    if citations:
        lines.extend(["## Evidence"])
        lines.extend(
            f"- {citation.title}"
            + (f" ({citation.location})" if citation.location else "")
            + f": {citation.snippet or 'Reference available.'}"
            for citation in citations
        )
        lines.append("")
    if uncertainty:
        lines.extend(["## Cautions", uncertainty, ""])
    return "\n".join(lines).strip()


def _build_actions(
    run_id: str, message_id: str, summary: str, has_sources: bool, has_analysis: bool
) -> list[dict[str, Any]]:
    actions = [
        {
            "id": f"download-{run_id}",
            "kind": "download_report",
            "label": "Open report",
            "icon": "download",
            "payload": {
                "url": _report_download_url(run_id, "html"),
                "pdf_url": _report_download_url(run_id, "pdf"),
                "markdown_url": _report_download_url(run_id, "markdown"),
            },
        },
        {
            "id": f"pdf-{run_id}",
            "kind": "download_pdf",
            "label": "Download PDF",
            "icon": "download",
            "payload": {"url": _report_download_url(run_id, "pdf")},
        },
        {
            "id": f"copy-{message_id}",
            "kind": "copy_summary",
            "label": "Copy summary",
            "icon": "copy",
            "payload": {"text": summary},
        },
        {
            "id": f"export-{message_id}",
            "kind": "export_summary",
            "label": "Export summary",
            "icon": "download",
            "payload": {"filename": f"qurultai-summary-{message_id[:8]}.txt", "text": summary},
        },
    ]
    if has_sources:
        actions.append(
            {
                "id": f"sources-{message_id}",
                "kind": "open_sources",
                "label": "Open sources",
                "icon": "reference",
                "payload": {"message_id": message_id},
            }
        )
    if has_analysis:
        actions.append(
            {
                "id": f"analysis-{message_id}",
                "kind": "expand_analysis",
                "label": "Expand analysis",
                "icon": "view",
                "payload": {"message_id": message_id},
            }
        )
    return actions


def _final_answer_prompt(
    *,
    mode: str,
    question: str,
    citations: list[CitationRead],
    specialist_notes: list[str],
) -> str:
    evidence_block = (
        "\n".join(
            f"- {citation.title}: {citation.snippet or 'Reference available.'}"
            for citation in citations
        )
        or "- No direct evidence retrieved."
    )
    specialist_block = "\n\n".join(specialist_notes) or "No specialist notes were required."
    return (
        f"The orchestration mode is '{mode}'. Prepare the final user-facing answer.\n\n"
        f"Question:\n{question}\n\n"
        f"Evidence:\n{evidence_block}\n\n"
        f"Specialist Notes:\n{specialist_block}"
    )


def _stream_answer_markdown(
    *,
    mode: str,
    question: str,
    context: str,
    citations: list[CitationRead],
    specialist_notes: list[str],
    selected_agents: list[ChatParticipantRead],
    uncertainty_note: str | None,
    max_output_tokens: int,
    on_delta: Callable[[str], None] | None = None,
) -> str:
    fallback = (
        "## Short answer\n\n"
        + (
            f"Based on the uploaded material, the strongest grounded direction is to focus on **{citations[0].title}** first. "
            if citations
            else "This looks straightforward enough to answer directly without escalating to a full council. "
        )
        + (
            "\n\n## Why this matters\n\nRelevant specialists were pulled in only where they added domain value. "
            if selected_agents
            else ""
        )
        + (f"\n\n## Watchouts\n\n- {uncertainty_note}" if uncertainty_note else "")
    ).strip()
    prompt = _final_answer_prompt(
        mode=mode,
        question=question,
        citations=citations,
        specialist_notes=specialist_notes,
    )
    system_prompt = (
        ASSISTANT_SYSTEM_PROMPT
        + "\n\nReturn only polished GitHub-flavored markdown for the final answer. Use short paragraphs, meaningful headings, "
        "and concise bullets where helpful. Do not wrap the response in JSON. "
        f"Target roughly {max_output_tokens} tokens or fewer, with strong compression rather than padding."
    )

    chunks: list[str] = []
    try:
        for delta in llm_service.stream_llm_with_context(
            prompt=prompt,
            system_prompt=system_prompt,
            context=context,
            max_output_tokens=max_output_tokens,
        ):
            if not delta:
                continue
            chunks.append(delta)
            if on_delta is not None:
                on_delta(delta)
    except Exception:
        fallback_answer = _safe_llm(
            prompt=prompt,
            fallback=fallback,
            system_prompt=system_prompt,
            context=context,
            max_output_tokens=max_output_tokens,
        )
        if on_delta is not None and fallback_answer:
            on_delta(fallback_answer)
        return fallback_answer

    answer = "".join(chunks).strip()
    if answer:
        return answer

    if on_delta is not None and fallback:
        on_delta(fallback)
    return fallback


def _recent_messages(session: Session, session_id: str) -> list[ChatMessage]:
    return list(
        session.exec(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
    )


def send_message(
    session: Session,
    *,
    session_id: str,
    content: str,
    mode_preference: ChatModePreference = "auto",
    attachments: list[tuple[bytes, str, str]] | None = None,
) -> tuple[Room, ChatRun]:
    room = _session_or_404(session, session_id)
    text = content.strip()
    if not text:
        raise ValueError("Message content cannot be empty.")

    user_message = ChatMessage(
        session_id=room.id,
        role="user",
        message_type="message",
        content=text,
        metadata_json={"mode_preference": mode_preference},
        status="completed",
    )
    session.add(user_message)
    session.commit()
    session.refresh(user_message)

    uploaded_documents: list[KnowledgeDocument] = []
    for payload, filename, mime_type in attachments or []:
        document, _chunks = knowledge_service.upload_document(
            session,
            source_filename=filename,
            payload=payload,
            mime_type=mime_type,
            title=filename,
            metadata={
                "source": "chat_attachment",
                "room_id": room.id,
                "message_id": user_message.id,
            },
        )
        uploaded_documents.append(document)
        existing = session.exec(
            select(RoomDocumentLink).where(
                RoomDocumentLink.room_id == room.id, RoomDocumentLink.document_id == document.id
            )
        ).first()
        if existing is None:
            session.add(RoomDocumentLink(room_id=room.id, document_id=document.id))
            session.commit()

    if uploaded_documents:
        user_message.attachments_json = [
            _message_attachment_from_document(document).model_dump(mode="json")
            for document in uploaded_documents
        ]
        session.add(user_message)
        session.commit()
        session.refresh(user_message)

    if not room.initial_query:
        room.initial_query = text
    if room.title == "New chat":
        room.title = _slug_title(text)
    room.last_message_preview = _truncate(text, limit=180)
    session.add(room)
    session.commit()
    session.refresh(room)

    assistant_message = ChatMessage(
        session_id=room.id,
        role="assistant",
        message_type="answer",
        content="",
        status="processing",
        metadata_json={"streaming": True},
    )
    session.add(assistant_message)
    session.commit()
    session.refresh(assistant_message)

    mode, selected_agents, diagnostics = _classify_request(
        session,
        room,
        text,
        uploaded_documents,
        mode_preference=mode_preference,
    )
    run = ChatRun(
        session_id=room.id,
        input_message_id=user_message.id,
        output_message_id=assistant_message.id,
        mode=mode,
        status="queued",
        selected_agents_json=[
            participant.model_dump(mode="json") for participant in selected_agents
        ],
        summary_json=diagnostics,
    )
    session.add(run)
    session.commit()
    session.refresh(run)

    assistant_message.run_id = run.id
    session.add(assistant_message)
    session.commit()

    append_run_event(
        session,
        run.id,
        "run_created",
        {
            "session_id": room.id,
            "mode": mode,
            "mode_preference": mode_preference,
            "message_id": user_message.id,
            "attachments": len(uploaded_documents),
            "diagnostics": diagnostics,
        },
    )
    append_run_event(
        session,
        run.id,
        "mode_selected",
        {
            "mode": mode,
            "mode_preference": mode_preference,
            "selected_agents": [
                participant.model_dump(mode="json") for participant in selected_agents
            ],
        },
    )

    return room, run


def claim_run_for_processing(run_id: str) -> bool:
    with SessionLocal() as session:
        run = _run_or_404(session, run_id)
        if run.status != "queued":
            return False
        run.status = "processing"
        run.started_at = utc_now()
        session.add(run)
        session.commit()
    return True


def _agent_analysis(
    *,
    agent: Agent,
    question: str,
    context: str,
    citations: list[CitationRead],
) -> SpecialistAnalysis:
    evidence_block = (
        "\n".join(
            f"- {citation.title}: {citation.snippet or 'Reference available.'}"
            for citation in citations
        )
        or "- No relevant citations were retrieved."
    )
    fallback = (
        f"{agent.name} recommends a measured approach within the scope of {agent.role_description.lower()}. "
        "Proceed with explicit assumptions, surface the main risk, and keep the evidence trail visible."
    )
    structured = _safe_structured_llm(
        prompt=(
            "Analyze the request from your specialist perspective and return structured output.\n\n"
            f"Question:\n{question}\n\nEvidence:\n{evidence_block}"
        ),
        response_model=SpecialistAnalysis,
        fallback=SpecialistAnalysis(
            summary=fallback,
            key_findings=[],
            risks=["Evidence may still be incomplete."],
            recommendation="Proceed with explicit assumptions and traceable evidence.",
        ),
        system_prompt=agent.system_prompt or SPECIALIST_PROMPT,
        context=context,
        skills_content=[skill.content_md for skill in agent.skills],
        max_output_tokens=_specialist_message_budget(question),
    )
    return structured


def _confidence_label(
    mode: str, citations: list[CitationRead], selected_agents: list[ChatParticipantRead]
) -> str:
    if mode == "direct_answer" and not citations:
        return "medium"
    if citations and (mode in {"rag_answer", "specialist_assist"}):
        return "high"
    if mode == "council" and selected_agents:
        return "medium-high"
    return "medium"


def _uncertainty_note(mode: str, citations: list[CitationRead]) -> str | None:
    if mode == "direct_answer":
        return None
    if not citations:
        return "The answer had to rely more on general reasoning because no strong session evidence surfaced."
    if len(citations) == 1:
        return "Most of the grounding came from a narrow source set, so it is worth checking whether other documents add constraints."
    return None


def _analysis_html(notes: list[str], critic_note: str | None) -> str | None:
    blocks = []
    for index, note in enumerate(notes, start=1):
        blocks.append(f"<section><h5>Analysis {index}</h5><p>{html.escape(note)}</p></section>")
    if critic_note:
        blocks.append(f"<section><h5>Quality check</h5><p>{html.escape(critic_note)}</p></section>")
    if not blocks:
        return None
    return "".join(blocks)


def _final_answer(
    *,
    mode: str,
    question: str,
    context: str,
    citations: list[CitationRead],
    specialist_notes: list[str],
    selected_agents: list[ChatParticipantRead],
    uncertainty_note: str | None,
    draft_answer_markdown: str | None = None,
    max_output_tokens: int,
) -> FinalAnswerPayload:
    fallback = (
        draft_answer_markdown.strip()
        if draft_answer_markdown and draft_answer_markdown.strip()
        else (
            "## Short answer\n\n"
            + (
                f"Based on the uploaded material, the strongest grounded direction is to focus on **{citations[0].title}** first. "
                if citations
                else "This looks straightforward enough to answer directly without escalating to a full council. "
            )
            + (
                "\n\n## Why this matters\n\nRelevant specialists were pulled in only where they added domain value. "
                if selected_agents
                else ""
            )
            + (f"\n\n## Watchouts\n\n- {uncertainty_note}" if uncertainty_note else "")
        )
    ).strip()
    prompt = _final_answer_prompt(
        mode=mode,
        question=question,
        citations=citations,
        specialist_notes=specialist_notes,
    )
    if draft_answer_markdown and draft_answer_markdown.strip():
        prompt += (
            "\n\nDraft answer markdown:\n"
            f"{draft_answer_markdown.strip()}\n\n"
            "Use the draft answer as the primary basis for `answer_markdown`. Tighten the structure and clarity, "
            "but keep the substance aligned unless the evidence clearly requires correction."
        )
    return _safe_structured_llm(
        prompt=prompt,
        response_model=FinalAnswerPayload,
        fallback=FinalAnswerPayload(
            answer_markdown=fallback,
            summary=_truncate(fallback, limit=220) or fallback,
            key_points=[],
            risks=[],
            recommendations=[],
            uncertainty=uncertainty_note,
            suggested_next_steps=[],
            report_title="Qurultai Report",
        ),
        system_prompt=(
            ASSISTANT_SYSTEM_PROMPT
            + "\n\nReturn `answer_markdown` as polished GitHub-flavored markdown with short paragraphs, clear headings when useful, "
            "and bullets for risks or actions. Avoid walls of text. Prefer a professional brief style. "
            f"Keep the full structured response within about {max_output_tokens} tokens."
        ),
        context=context,
        max_output_tokens=max_output_tokens,
    )


def _emit_answer_stream(session: Session, run_id: str, message: ChatMessageRead) -> None:
    content = message.content.strip()
    if not content:
        append_run_event(
            session,
            run_id,
            "assistant_message_completed",
            {"message": message.model_dump(mode="json")},
        )
        return

    chunk_size = 140
    for index in range(0, len(content), chunk_size):
        append_run_event(
            session,
            run_id,
            "assistant_message_delta",
            {"message_id": message.id, "delta": content[index : index + chunk_size]},
        )
    append_run_event(
        session,
        run_id,
        "assistant_message_completed",
        {"message": message.model_dump(mode="json")},
    )


def process_run(run_id: str) -> None:
    with SessionLocal() as session:
        run = _run_or_404(session, run_id)
        if run.status not in {"processing", "queued"}:
            return

        room = _session_or_404(session, run.session_id)
        input_message = _message_or_404(session, run.input_message_id)
        output_message = _message_or_404(session, run.output_message_id or "")
        all_messages = _recent_messages(session, room.id)
        context = _recent_conversation(all_messages[:-1], limit=10)

        try:
            if run.status != "processing":
                run.status = "processing"
                run.started_at = utc_now()
                session.add(run)
                session.commit()
            append_run_event(session, run.id, "run_status_changed", {"status": "processing"})

            citations = _session_citations(session, room, input_message.content, limit=6)
            answer_token_budget = _mode_output_budget(
                mode=run.mode,
                question=input_message.content,
                docs_present=bool(citations),
                participant_count=len(run.selected_agents_json or []),
            )
            append_run_event(
                session,
                run.id,
                "retrieval_completed",
                {
                    "citation_count": len(citations),
                    "sources": [citation.model_dump(mode="json") for citation in citations],
                },
            )

            selected_agents = [
                ChatParticipantRead.model_validate(item) for item in run.selected_agents_json or []
            ]
            agent_map = {agent.id: agent for agent in _active_agents(session)}

            if selected_agents:
                orchestrator_message = _debate_message_payload(
                    run_id=run.id,
                    role="orchestrator",
                    source_agent_id=None,
                    source_agent_name="Qurultai Orchestrator",
                    stage="orchestration",
                    content=(
                        f"Routing selected **{run.mode.replace('_', ' ')}** mode and brought in "
                        f"{len(selected_agents)} institution{'s' if len(selected_agents) != 1 else ''} "
                        "to test the question from distinct operational angles."
                    ),
                )
                append_run_event(
                    session,
                    run.id,
                    "agent_message_final",
                    {"message": orchestrator_message},
                )

            specialist_notes: list[str] = []
            if run.mode in {"specialist_assist", "council"}:
                for participant in selected_agents:
                    append_run_event(
                        session,
                        run.id,
                        "agent_selected",
                        {"participant": participant.model_dump(mode="json")},
                    )
                    agent = agent_map.get(participant.id)
                    if agent is None:
                        continue
                    append_run_event(
                        session,
                        run.id,
                        "agent_started",
                        {"participant": participant.model_dump(mode="json")},
                    )
                    append_run_event(
                        session,
                        run.id,
                        "tool_called",
                        {
                            "agent_id": agent.id,
                            "tool": _tool_call_payload(
                                name="session_evidence_review",
                                status="running",
                                input_payload={"query": input_message.content},
                            ),
                        },
                    )
                    analysis = _agent_analysis(
                        agent=agent,
                        question=input_message.content,
                        context=context,
                        citations=citations,
                    )
                    specialist_markdown = _analysis_to_markdown(analysis)
                    note = _analysis_to_note(analysis)
                    specialist_notes.append(note)
                    tool_calls = [
                        _tool_call_payload(
                            name="session_evidence_review",
                            status="completed",
                            input_payload={"query": input_message.content},
                            output_summary=(
                                f"Reviewed {len(citations)} supporting source"
                                f"{'s' if len(citations) != 1 else ''} for this position."
                            ),
                        )
                    ]
                    append_run_event(
                        session,
                        run.id,
                        "tool_result",
                        {
                            "agent_id": agent.id,
                            "tool": tool_calls[0],
                        },
                    )
                    debate_message = _debate_message_payload(
                        run_id=run.id,
                        role="agent",
                        source_agent_id=agent.id,
                        source_agent_name=agent.name,
                        stage="analysis",
                        content=specialist_markdown,
                        citations=citations[:3],
                        tool_calls=tool_calls,
                    )
                    _emit_debate_message_stream(session, run_id=run.id, message=debate_message)
                    append_run_event(
                        session,
                        run.id,
                        "agent_completed",
                        {
                            "participant": participant.model_dump(mode="json"),
                            "summary": _truncate(note, limit=240),
                        },
                    )

            critic_note: str | None = None
            if run.mode == "council" and specialist_notes:
                append_run_event(
                    session,
                    run.id,
                    "critic_started",
                    {"summary": "A critic pass is checking for overconfidence, conflict, and missing constraints."},
                )
                critic_note = _safe_llm(
                    prompt=(
                        "Review the specialist notes for contradictions, missing evidence, or overconfident claims. "
                        "Respond in 2-3 short paragraphs with explicit cautions and no fluff."
                    ),
                    context="\n\n".join(specialist_notes),
                    fallback=(
                        "The specialist notes are broadly aligned, but the main risk is overstating certainty where the cited evidence is still narrow."
                    ),
                    max_output_tokens=get_settings().OPENAI_MAX_OUTPUT_TOKENS_CRITIC,
                )
                critic_message = _debate_message_payload(
                    run_id=run.id,
                    role="critic",
                    source_agent_id=None,
                    source_agent_name="Cross-check Critic",
                    stage="critique",
                    content=critic_note,
                    citations=citations[:2],
                )
                _emit_debate_message_stream(session, run_id=run.id, message=critic_message)
                append_run_event(
                    session,
                    run.id,
                    "quality_check_completed",
                    {"summary": critic_note},
                )

            uncertainty = _uncertainty_note(run.mode, citations)

            streamed_chunks: list[str] = []
            buffered_persist = ""

            def handle_answer_delta(delta: str) -> None:
                nonlocal buffered_persist
                if not delta:
                    return
                streamed_chunks.append(delta)
                append_run_event(
                    session,
                    run.id,
                    "assistant_message_delta",
                    {"message_id": output_message.id, "delta": delta},
                )
                buffered_persist += delta
                if len(buffered_persist) >= 240 or delta.endswith("\n"):
                    output_message.content = "".join(streamed_chunks)
                    output_message.metadata_json = {
                        **dict(output_message.metadata_json or {}),
                        "streaming": True,
                    }
                    session.add(output_message)
                    session.commit()
                    buffered_persist = ""

            draft_answer = _stream_answer_markdown(
                mode=run.mode,
                question=input_message.content,
                context=context,
                citations=citations,
                specialist_notes=specialist_notes,
                selected_agents=selected_agents,
                uncertainty_note=uncertainty,
                max_output_tokens=answer_token_budget,
                on_delta=handle_answer_delta,
            )
            if buffered_persist:
                output_message.content = "".join(streamed_chunks)
                output_message.metadata_json = {
                    **dict(output_message.metadata_json or {}),
                    "streaming": True,
                }
                session.add(output_message)
                session.commit()

            final_answer_payload = _final_answer(
                mode=run.mode,
                question=input_message.content,
                context=context,
                citations=citations,
                specialist_notes=specialist_notes,
                selected_agents=selected_agents,
                uncertainty_note=uncertainty,
                draft_answer_markdown=draft_answer,
                max_output_tokens=answer_token_budget + 220,
            )
            answer = final_answer_payload.answer_markdown
            confidence = _confidence_label(run.mode, citations, selected_agents)
            analysis_html = _analysis_html(specialist_notes, critic_note)
            report_title = final_answer_payload.report_title.strip() or "Qurultai Report"
            report_md = _report_markdown(
                question=input_message.content,
                answer_payload=final_answer_payload,
                citations=citations,
                participants=selected_agents,
                mode=run.mode,
                confidence=confidence,
                uncertainty=final_answer_payload.uncertainty,
            )
            report_stats = [
                ("Mode", run.mode.replace("_", " ")),
                ("Confidence", confidence),
                ("Sources", str(len(citations))),
                ("Institutions", str(len(selected_agents))),
            ]
            report_html = report_service.render_report_html(
                report_md,
                title=report_title,
                subtitle=final_answer_payload.summary,
                stats=report_stats,
            )
            report_service.write_report_artifacts(
                run.id,
                report_md,
                title=report_title,
                subtitle=final_answer_payload.summary,
                stats=report_stats,
            )

            output_message.content = answer
            output_message.html_content = _render_message_html(
                answer_payload=final_answer_payload,
                citations=citations,
                participants=selected_agents,
                confidence=confidence,
                uncertainty=uncertainty,
                mode=run.mode,
                analysis_html=analysis_html,
            )
            output_message.citations_json = [
                citation.model_dump(mode="json") for citation in citations
            ]
            output_message.actions_json = _build_actions(
                run.id,
                output_message.id,
                final_answer_payload.summary,
                has_sources=bool(citations),
                has_analysis=analysis_html is not None,
            )
            output_message.metadata_json = {
                "mode": run.mode,
                "confidence": confidence,
                "uncertainty": final_answer_payload.uncertainty,
                "participants": [
                    participant.model_dump(mode="json") for participant in selected_agents
                ],
                "analysis_html": analysis_html,
                "report_title": report_title,
                "key_points": final_answer_payload.key_points,
                "risks": final_answer_payload.risks,
                "recommendations": final_answer_payload.recommendations,
                "suggested_next_steps": final_answer_payload.suggested_next_steps,
                "report_downloads": {
                    "markdown": _report_download_url(run.id, "markdown"),
                    "html": _report_download_url(run.id, "html"),
                    "pdf": _report_download_url(run.id, "pdf"),
                },
            }
            output_message.status = "completed"
            session.add(output_message)

            run.status = "completed"
            run.finished_at = utc_now()
            run.final_report_title = report_title
            run.final_report_md = report_md
            run.final_report_html = report_html
            run.summary_json = {
                **dict(run.summary_json or {}),
                "confidence": confidence,
                "citation_count": len(citations),
                "summary": final_answer_payload.summary,
            }
            session.add(run)

            room.last_message_preview = _truncate(final_answer_payload.summary, limit=180)
            room.final_report_md = report_md
            room.context_text = _recent_conversation(_recent_messages(session, room.id), limit=12)
            session.add(room)
            session.commit()
            session.refresh(output_message)

            append_run_event(
                session,
                run.id,
                "assistant_message_completed",
                {"message": _message_read(output_message).model_dump(mode="json")},
            )
            append_run_event(
                session,
                run.id,
                "report_ready",
                {
                    "markdown_url": _report_download_url(run.id, "markdown"),
                    "html_url": _report_download_url(run.id, "html"),
                    "pdf_url": _report_download_url(run.id, "pdf"),
                },
            )
            append_run_event(session, run.id, "run_status_changed", {"status": "completed"})
            append_run_event(session, run.id, "run_completed", {"status": "completed"})
        except Exception as exc:
            output_message.content = "I ran into a problem while preparing the answer."
            output_message.html_content = None
            output_message.citations_json = []
            output_message.actions_json = []
            output_message.metadata_json = {"error": str(exc)}
            output_message.status = "failed"
            session.add(output_message)

            run.status = "failed"
            run.finished_at = utc_now()
            session.add(run)

            room.last_message_preview = "Run failed"
            session.add(room)
            session.commit()

            append_run_event(
                session,
                run.id,
                "run_failed",
                {"status": "failed", "error": str(exc)},
            )


def get_run_read(session: Session, run_id: str) -> ChatRunRead:
    return _run_read(session, _run_or_404(session, run_id))


def load_report_bytes(session: Session, run_id: str, format_name: str) -> tuple[bytes, str, str]:
    run = _run_or_404(session, run_id)
    format_key = format_name.lower()
    if format_key == "markdown":
        return (
            (run.final_report_md or "").encode("utf-8"),
            "text/markdown; charset=utf-8",
            f"chat-run-{run_id}.md",
        )
    html_path, pdf_path = report_service.artifact_paths(run_id)
    if format_key == "html":
        if not html_path.exists() and run.final_report_md:
            report_service.write_report_artifacts(
                run.id, run.final_report_md, title="Qurultai Report"
            )
        return html_path.read_bytes(), "text/html; charset=utf-8", f"chat-run-{run_id}.html"
    if format_key == "pdf":
        if not pdf_path.exists() and run.final_report_md:
            report_service.write_report_artifacts(
                run.id, run.final_report_md, title="Qurultai Report"
            )
        if not pdf_path.exists():
            raise NotFoundError("PDF report is not available for this run.")
        return pdf_path.read_bytes(), "application/pdf", f"chat-run-{run_id}.pdf"
    raise NotFoundError(f"Unsupported report format '{format_name}'.")
