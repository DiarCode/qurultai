from __future__ import annotations

import time
from typing import Any
from uuid import uuid4

from sqlmodel import Session, func, select

from app.core.exceptions import NotFoundError
from app.core.utils import utc_now
from app.db.session import SessionLocal
from app.models.agent import Agent
from app.models.agent_run import AgentRun
from app.models.agent_source import AgentSource
from app.models.agent_step import AgentStep
from app.models.knowledge_document import KnowledgeDocument
from app.models.room import Room
from app.models.room_event import RoomDocumentLink, RoomEvent
from app.schemas.runs import (
    CitationRead,
    FileReferenceRead,
    ReportVariantRead,
    RunEventRead,
    RunMessageRead,
    RunParticipantRead,
    RunRead,
    RunReportRead,
    ToolCallRead,
)
from app.services import knowledge_service, llm_service, report_service, room_service, s3_service


def _room_or_404(session: Session, room_id: str) -> Room:
    room = session.get(Room, room_id)
    if room is None:
        raise NotFoundError(f"Run '{room_id}' was not found.")
    return room


def _download_url(document_id: str) -> str:
    return f"/api/v1/files/{document_id}/download"


def _build_file_reference(
    document: KnowledgeDocument, *, linked_entity_type: str, linked_entity_id: str
) -> FileReferenceRead:
    metadata = document.metadata_json or {}
    return FileReferenceRead(
        id=document.id,
        name=document.title or document.source_filename,
        mime_type=document.mime_type,
        size_bytes=document.size_bytes,
        linked_entity_type=linked_entity_type,
        linked_entity_id=linked_entity_id,
        created_at=document.created_at,
        download_url=_download_url(document.id),
        text_preview=document.text_preview,
        upload_status=str(metadata.get("upload_status") or "completed"),
        index_status=str(metadata.get("index_status") or "completed"),
        chunk_count=int(metadata.get("chunk_count") or 0),
        parser_kind=str(metadata.get("parser_kind")) if metadata.get("parser_kind") else None,
    )


def _build_citation(
    document: KnowledgeDocument,
    snippet: str | None,
    score: float | None,
    *,
    location: str | None = None,
) -> CitationRead:
    return CitationRead(
        id=f"citation-{document.id}",
        document_id=document.id,
        title=document.title,
        snippet=snippet,
        score=score,
        location=location
        or (document.metadata_json.get("location") if document.metadata_json else None),
        download_url=_download_url(document.id),
    )


def _parse_report_summary(report_md: str) -> str:
    for block in report_md.split("\n\n"):
        stripped = block.strip()
        if not stripped or stripped.startswith("#"):
            continue
        return stripped
    return "Council report prepared."


def create_run(
    session: Session,
    *,
    prompt: str,
    attachments: list[tuple[bytes, str, str]] | None = None,
) -> Room:
    room = Room(initial_query=prompt, status="queued")
    session.add(room)
    session.commit()
    session.refresh(room)

    for payload, filename, mime_type in attachments or []:
        document, _chunks_ingested = knowledge_service.upload_document(
            session,
            source_filename=filename,
            payload=payload,
            mime_type=mime_type,
            title=filename,
            metadata={"source": "run_attachment", "room_id": room.id},
        )
        session.add(RoomDocumentLink(room_id=room.id, document_id=document.id))
        session.commit()

    append_event(
        session,
        room.id,
        "run_created",
        {
            "run_id": room.id,
            "status": room.status,
            "prompt": room.initial_query,
            "attachment_count": len(attachments or []),
        },
    )
    return room


def list_run_attachments(session: Session, run_id: str) -> list[KnowledgeDocument]:
    _room_or_404(session, run_id)
    links = list(session.exec(select(RoomDocumentLink).where(RoomDocumentLink.room_id == run_id)))
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


def append_event(
    session: Session, run_id: str, event_type: str, payload: dict[str, Any]
) -> RoomEvent:
    sequence = (
        session.exec(select(func.max(RoomEvent.sequence)).where(RoomEvent.room_id == run_id)).one()
        or 0
    )
    event = RoomEvent(
        room_id=run_id,
        sequence=int(sequence) + 1,
        event_type=event_type,
        payload_json=payload,
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def list_events(session: Session, run_id: str, after_sequence: int = 0) -> list[RoomEvent]:
    _room_or_404(session, run_id)
    return list(
        session.exec(
            select(RoomEvent)
            .where(RoomEvent.room_id == run_id, RoomEvent.sequence > after_sequence)
            .order_by(RoomEvent.sequence.asc())
        )
    )


def _participant_read(agent: Agent) -> RunParticipantRead:
    return RunParticipantRead(
        id=agent.id,
        key=agent.key,
        name=agent.name,
        role=agent.role_description,
        status=agent.status,
    )


def _log_run_step(
    session: Session,
    *,
    run_id: str,
    step_type: str,
    content: dict[str, Any] | str,
    citations: list[CitationRead],
) -> None:
    step = AgentStep(run_id=run_id, step_type=step_type, content_json=content)
    session.add(step)
    session.flush()

    for citation in citations:
        session.add(
            AgentSource(
                step_id=step.id,
                source_type="KNOWLEDGE_DOCUMENT",
                ref_id=citation.document_id,
                snippet=citation.snippet,
                score=citation.score,
            )
        )

    session.commit()


def _safe_llm(
    prompt: str,
    *,
    system_prompt: str | None = None,
    context: str | None = None,
    skills_content: list[str] | None = None,
    fallback: str,
) -> str:
    try:
        response = llm_service.invoke_llm_with_context(
            prompt=prompt,
            system_prompt=system_prompt,
            context=context,
            skills_content=skills_content,
        )
        return response.strip() or fallback
    except Exception:
        return fallback


def _select_agents(session: Session, prompt: str) -> list[Agent]:
    agents = list(
        session.exec(
            select(Agent)
            .where(Agent.status.in_(["active", "draft"]))
            .order_by(Agent.created_at.asc())
        )
    )
    if not agents:
        return []

    prompt_tokens = {token.lower() for token in prompt.split() if len(token) >= 4}
    scored: list[tuple[int, Agent]] = []
    for agent in agents:
        haystack = f"{agent.name} {agent.role_description} {agent.description or ''} {agent.system_prompt}".lower()
        score = sum(1 for token in prompt_tokens if token in haystack)
        scored.append((score, agent))

    scored.sort(key=lambda item: item[0], reverse=True)
    selected = [agent for _score, agent in scored[: min(4, len(scored))]]
    return selected or agents[:3]


def _search_references(session: Session, query: str, agent_id: str | None) -> list[CitationRead]:
    hits = knowledge_service.search_documents(session, query=query, limit=4, agent_id=agent_id)
    if not hits and agent_id is not None:
        hits = knowledge_service.search_documents(session, query=query, limit=4, agent_id=None)

    citations: list[CitationRead] = []
    for hit in hits:
        document_id = str(hit.get("document_id") or "")
        if not document_id:
            continue
        document = session.get(KnowledgeDocument, document_id)
        if document is None:
            continue
        citations.append(
            _build_citation(
                document,
                str(hit.get("text") or "")[:260],
                float(hit.get("score") or 0.0),
                location=str(hit.get("location") or "") or None,
            )
        )
    return citations


def _chunk_text(text: str, size: int = 90) -> list[str]:
    if not text:
        return []
    return [text[index : index + size] for index in range(0, len(text), size)]


def _emit_message_stream(
    session: Session,
    *,
    run_id: str,
    message: RunMessageRead,
) -> None:
    for chunk in _chunk_text(message.content):
        append_event(
            session,
            run_id,
            "agent_message_delta",
            {
                "message_id": message.id,
                "role": message.role,
                "source_agent_id": message.source_agent_id,
                "source_agent_name": message.source_agent_name,
                "stage": message.stage,
                "delta": chunk,
            },
        )
        time.sleep(0.02)

    append_event(
        session, run_id, "agent_message_final", {"message": message.model_dump(mode="json")}
    )


def _report_variants(run_id: str) -> list[ReportVariantRead]:
    variants = [
        ReportVariantRead(
            format="markdown",
            download_url=f"/api/v1/runs/{run_id}/report/download?format=markdown",
        ),
        ReportVariantRead(
            format="html",
            download_url=f"/api/v1/runs/{run_id}/report/download?format=html",
        ),
    ]

    _html_path, pdf_path = room_service._artifact_paths(run_id)
    if pdf_path.exists():
        variants.append(
            ReportVariantRead(
                format="pdf",
                download_url=f"/api/v1/runs/{run_id}/report/download?format=pdf",
            )
        )
    return variants


def _generate_report(
    *,
    room: Room,
    specialist_messages: list[RunMessageRead],
    critic_message: RunMessageRead | None,
    attachments: list[KnowledgeDocument],
) -> str:
    evidence_lines: list[str] = []
    for message in specialist_messages:
        for citation in message.citations:
            location = f" ({citation.location})" if citation.location else ""
            evidence_lines.append(
                f"- {citation.title}{location}: {citation.snippet or 'Reference available.'}"
            )

    attachment_lines = []
    for attachment in attachments:
        metadata = attachment.metadata_json or {}
        attachment_lines.append(
            "- "
            f"{attachment.title} · {metadata.get('upload_status', 'completed')} upload · "
            f"{metadata.get('index_status', 'completed')} indexing · "
            f"{metadata.get('chunk_count', 0)} chunks"
        )
    summary = " ".join(message.content for message in specialist_messages[:2]).strip()
    summary = summary[:360] if summary else "Council completed a coordinated review."

    fallback_sections = [
        "# Council Report",
        "",
        "## Executive Summary",
        summary,
        "",
        "## Specialist Deliberation",
    ]

    for message in specialist_messages:
        fallback_sections.extend(
            [
                f"### {message.source_agent_name}",
                message.content,
                "",
            ]
        )

    if critic_message is not None:
        fallback_sections.extend(["## Critic Review", critic_message.content, ""])

    if attachment_lines:
        fallback_sections.extend(["## Submitted Documents", *attachment_lines, ""])

    if evidence_lines:
        fallback_sections.extend(["## Evidence", *evidence_lines, ""])

    fallback_sections.extend(
        [
            "## Final Recommendation",
            "Proceed in phased delivery, preserve traceable evidence in every answer, and keep disagreement visibility in the council audit trail.",
        ]
    )
    fallback_report = "\n".join(fallback_sections).strip()

    report_context = "\n\n".join(
        [
            f"User Request:\n{room.initial_query}",
            "Specialist Positions:\n"
            + "\n\n".join(
                f"{message.source_agent_name}:\n{message.content}"
                for message in specialist_messages
            ),
            f"Critic Review:\n{critic_message.content if critic_message is not None else 'No critic review provided.'}",
            "Submitted Documents:\n"
            + ("\n".join(attachment_lines) if attachment_lines else "- No uploaded documents."),
            "Evidence Ledger:\n"
            + ("\n".join(evidence_lines) if evidence_lines else "- No indexed evidence."),
        ]
    )

    return _safe_llm(
        prompt=(
            "Write a polished final council report in Markdown with these sections in order: "
            "Executive Summary, Council Deliberation, Critic Review, Evidence Ledger, Final Recommendation. "
            "Use only public-facing reasoning, keep claims grounded in the evidence ledger, and mention unresolved risks."
        ),
        system_prompt=(
            "You are the final report agent for a government intelligence council. "
            "Produce concise, formal, traceable Markdown reports."
        ),
        context=report_context,
        fallback=fallback_report,
    )


def _build_report_read(room: Room) -> RunReportRead | None:
    if not room.final_report_md:
        return None
    return RunReportRead(
        title="Council Report",
        summary=_parse_report_summary(room.final_report_md),
        body_markdown=room.final_report_md,
        body_html=report_service.render_report_html(room.final_report_md, title="Council Report"),
        source_agent_name="Final Report Agent",
        generated_at=room.updated_at,
        variants=_report_variants(room.id),
    )


def process_run(run_id: str) -> None:
    with SessionLocal() as session:
        room = _room_or_404(session, run_id)
        attachments = list_run_attachments(session, run_id)

        try:
            room.status = "processing"
            room.context_text = "\n\n".join(
                [room.initial_query, *[attachment.text_preview or "" for attachment in attachments]]
            ).strip()
            session.add(room)
            session.commit()
            session.refresh(room)

            append_event(session, run_id, "run_status_changed", {"status": room.status})
            append_event(
                session,
                run_id,
                "orchestrator_started",
                {
                    "summary": "The orchestrator is selecting the council, grounding the request in uploaded evidence, and preparing a traceable run.",
                },
            )

            selected_agents = _select_agents(session, room.context_text or room.initial_query)
            specialist_messages: list[RunMessageRead] = []

            orchestrator_message = RunMessageRead(
                id=str(uuid4()),
                run_id=run_id,
                role="orchestrator",
                source_agent_name="Orchestrator",
                stage="orchestration",
                status="completed",
                content=f"Selected {len(selected_agents)} council participants and queued evidence retrieval.",
                created_at=utc_now(),
            )
            append_event(
                session,
                run_id,
                "agent_message_final",
                {"message": orchestrator_message.model_dump(mode="json")},
            )

            for agent in selected_agents:
                participant = _participant_read(agent)
                append_event(
                    session,
                    run_id,
                    "agent_selected",
                    {"participant": participant.model_dump(mode="json")},
                )

                agent_run = AgentRun(
                    room_id=run_id,
                    agent_id=agent.id,
                    status="processing",
                    bid_reason="Selected by council orchestrator",
                    started_at=utc_now(),
                )
                session.add(agent_run)
                session.commit()
                session.refresh(agent_run)

                append_event(
                    session,
                    run_id,
                    "agent_started",
                    {"participant": participant.model_dump(mode="json")},
                )
                append_event(
                    session,
                    run_id,
                    "retrieval_started",
                    {"agent_id": agent.id, "agent_name": agent.name},
                )

                citations = _search_references(
                    session, room.context_text or room.initial_query, agent.id
                )
                append_event(
                    session,
                    run_id,
                    "tool_called",
                    {
                        "agent_id": agent.id,
                        "tool": {
                            "name": "rag_search",
                            "status": "running",
                            "input": {"query": room.initial_query},
                        },
                    },
                )
                append_event(
                    session,
                    run_id,
                    "retrieval_finished",
                    {
                        "agent_id": agent.id,
                        "agent_name": agent.name,
                        "result_count": len(citations),
                    },
                )
                append_event(
                    session,
                    run_id,
                    "tool_result",
                    {
                        "agent_id": agent.id,
                        "tool": {
                            "name": "rag_search",
                            "status": "completed",
                            "input": {"query": room.initial_query},
                            "output_summary": f"Retrieved {len(citations)} supporting document snippets.",
                        },
                    },
                )

                for citation in citations:
                    append_event(
                        session,
                        run_id,
                        "citation_attached",
                        {
                            "agent_id": agent.id,
                            "citation": citation.model_dump(mode="json"),
                        },
                    )

                append_event(
                    session,
                    run_id,
                    "agent_thinking_visible_summary",
                    {
                        "agent_id": agent.id,
                        "agent_name": agent.name,
                        "summary": f"{agent.name} is weighing {agent.role_description.lower()} concerns against the retrieved evidence.",
                    },
                )

                evidence_block = "\n".join(
                    f"- {citation.title}: {citation.snippet or 'Document reference available.'}"
                    for citation in citations
                )
                fallback = (
                    f"{agent.name} reviewed the request through the lens of {agent.role_description.lower()}. "
                    "The recommendation is to proceed in phases, publish evidence for each claim, and keep unresolved risks explicit."
                )
                content = _safe_llm(
                    prompt=(
                        "Provide a concise public-facing specialist position with risks, recommendation, and cited evidence.\n\n"
                        f"Request:\n{room.initial_query}\n\n"
                        f"Evidence:\n{evidence_block or '- No indexed evidence available; rely on the uploaded brief and role mandate.'}"
                    ),
                    system_prompt=agent.system_prompt,
                    context=room.context_text,
                    skills_content=[skill.content_md for skill in agent.skills],
                    fallback=fallback,
                )

                tool_calls = [
                    ToolCallRead(
                        name="rag_search",
                        status="completed",
                        input={"query": room.initial_query},
                        output_summary=f"Retrieved {len(citations)} supporting snippets.",
                    )
                ]
                message = RunMessageRead(
                    id=str(uuid4()),
                    run_id=run_id,
                    role="agent",
                    source_agent_id=agent.id,
                    source_agent_name=agent.name,
                    stage="analysis",
                    status="completed",
                    content=content,
                    citations=citations,
                    tool_calls=tool_calls,
                    created_at=utc_now(),
                )
                _log_run_step(
                    session,
                    run_id=agent_run.id,
                    step_type="COUNCIL_MESSAGE",
                    content={"message": content},
                    citations=citations,
                )
                _emit_message_stream(session, run_id=run_id, message=message)
                specialist_messages.append(message)

                agent_run.status = "completed"
                agent_run.finished_at = utc_now()
                session.add(agent_run)
                session.commit()

            append_event(
                session,
                run_id,
                "critic_started",
                {
                    "summary": "The critic is checking the specialist positions for gaps and contradictions."
                },
            )

            critic_fallback = "The council positions are directionally aligned. The main remaining risk is execution drift unless evidence links stay visible throughout the rollout."
            critic_content = _safe_llm(
                prompt=(
                    "Review these council positions for contradictions, missing evidence, and weak claims. "
                    "Respond with a short public-facing critique.\n\n"
                    + "\n\n".join(
                        f"{message.source_agent_name}: {message.content}"
                        for message in specialist_messages
                    )
                ),
                context="Evidence ledger:\n"
                + "\n".join(
                    f"- {citation.title}: {citation.snippet or 'Reference available.'}"
                    for message in specialist_messages
                    for citation in message.citations
                ),
                fallback=critic_fallback,
            )
            critic_message = RunMessageRead(
                id=str(uuid4()),
                run_id=run_id,
                role="critic",
                source_agent_name="Critic",
                stage="critique",
                status="completed",
                content=critic_content,
                created_at=utc_now(),
            )
            _emit_message_stream(session, run_id=run_id, message=critic_message)

            append_event(
                session,
                run_id,
                "final_report_started",
                {
                    "summary": "The final report agent is consolidating the council record into a downloadable report."
                },
            )

            report_md = _generate_report(
                room=room,
                specialist_messages=specialist_messages,
                critic_message=critic_message,
                attachments=attachments,
            )
            room.final_report_md = report_md
            session.add(room)
            session.commit()
            room_service._write_artifacts(room, report_md)

            final_message = RunMessageRead(
                id=str(uuid4()),
                run_id=run_id,
                role="final",
                source_agent_name="Final Report Agent",
                stage="final_report",
                status="completed",
                content=_parse_report_summary(report_md),
                created_at=utc_now(),
            )
            append_event(
                session,
                run_id,
                "agent_message_final",
                {"message": final_message.model_dump(mode="json")},
            )

            report = _build_report_read(room)
            if report is not None:
                append_event(
                    session,
                    run_id,
                    "final_report_ready",
                    {"report": report.model_dump(mode="json")},
                )

            room.status = "completed"
            session.add(room)
            session.commit()
            session.refresh(room)
            append_event(session, run_id, "run_status_changed", {"status": room.status})
            append_event(session, run_id, "run_completed", {"status": room.status})
        except Exception as exc:
            room.status = "failed"
            room.final_report_md = (
                "# Council Run Failed\n\n"
                "The council run could not complete successfully.\n\n"
                f"Error: {exc}"
            )
            session.add(room)
            session.commit()
            append_event(session, run_id, "run_status_changed", {"status": room.status})
            append_event(session, run_id, "run_failed", {"status": room.status, "error": str(exc)})


def claim_run_for_processing(run_id: str) -> bool:
    with SessionLocal() as session:
        room = _room_or_404(session, run_id)
        if room.status != "queued":
            return False
        room.status = "processing"
        session.add(room)
        session.commit()
    return True


def _messages_from_events(events: list[RoomEvent]) -> list[RunMessageRead]:
    messages: list[RunMessageRead] = []
    seen_ids: set[str] = set()
    for event in events:
        if event.event_type != "agent_message_final":
            continue
        payload = event.payload_json.get("message")
        if not isinstance(payload, dict):
            continue
        message = RunMessageRead.model_validate(payload)
        if message.id in seen_ids:
            continue
        seen_ids.add(message.id)
        messages.append(message)
    messages.sort(key=lambda item: item.created_at)
    return messages


def _participants_from_events(events: list[RoomEvent]) -> list[RunParticipantRead]:
    participants: dict[str, RunParticipantRead] = {}
    for event in events:
        if event.event_type != "agent_selected":
            continue
        payload = event.payload_json.get("participant")
        if not isinstance(payload, dict):
            continue
        participant = RunParticipantRead.model_validate(payload)
        participants[participant.id] = participant
    return list(participants.values())


def build_run_read(session: Session, run_id: str, *, include_events: bool = True) -> RunRead:
    room = _room_or_404(session, run_id)
    events = list_events(session, run_id) if include_events else []
    event_reads = [
        RunEventRead(
            id=event.id,
            run_id=event.room_id,
            sequence=event.sequence,
            event_type=event.event_type,
            created_at=event.created_at,
            payload=event.payload_json,
        )
        for event in events
    ]
    attachments = [
        _build_file_reference(document, linked_entity_type="run", linked_entity_id=run_id)
        for document in list_run_attachments(session, run_id)
    ]
    return RunRead(
        id=room.id,
        prompt=room.initial_query,
        status=room.status,  # type: ignore[arg-type]
        created_at=room.created_at,
        updated_at=room.updated_at,
        participants=_participants_from_events(events),
        attachments=attachments,
        messages=_messages_from_events(events),
        final_report=_build_report_read(room),
        events=event_reads,
    )


def load_report_bytes(session: Session, run_id: str, format_name: str) -> tuple[bytes, str, str]:
    room = _room_or_404(session, run_id)
    format_key = format_name.lower()
    if format_key == "markdown":
        payload = (room.final_report_md or "").encode("utf-8")
        return payload, "text/markdown; charset=utf-8", f"run-{run_id}.md"

    html_path, pdf_path = room_service._artifact_paths(run_id)
    if format_key == "html":
        if not html_path.exists() and room.final_report_md:
            room_service._write_artifacts(room, room.final_report_md)
        return html_path.read_bytes(), "text/html; charset=utf-8", f"run-{run_id}.html"

    if format_key == "pdf":
        if not pdf_path.exists() and room.final_report_md:
            room_service._write_artifacts(room, room.final_report_md)
        if not pdf_path.exists():
            raise NotFoundError("PDF report is not available for this run.")
        return pdf_path.read_bytes(), "application/pdf", f"run-{run_id}.pdf"

    raise NotFoundError(f"Unsupported report format '{format_name}'.")


def load_document_bytes(session: Session, document_id: str) -> tuple[bytes, str, str]:
    document = knowledge_service.get_document(session, document_id)
    return (
        s3_service.download_bytes(document.s3_key),
        document.mime_type or "application/octet-stream",
        document.source_filename,
    )
