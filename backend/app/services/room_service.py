from __future__ import annotations

import html
import re
from collections import Counter
from pathlib import Path
from typing import Any

from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.document_parser import auto_parse_document
from app.core.exceptions import NotFoundError
from app.core.utils import ensure_directory, utc_now
from app.models.agent import Agent
from app.models.agent_run import AgentRun
from app.models.agent_source import AgentSource
from app.models.agent_step import AgentStep
from app.models.room import Room
from app.db.session import SessionLocal
from app.services import s3_service


def create_room(session: Session, query: str) -> Room:
    room = Room(initial_query=query, status="OPEN")
    session.add(room)
    session.commit()
    session.refresh(room)
    return room


def mark_room_processing(session: Session, room_id: str) -> Room:
    room = session.get(Room, room_id)
    if room is None:
        raise NotFoundError(f"Room '{room_id}' was not found.")
    room.status = "PROCESSING"
    session.add(room)
    session.commit()
    session.refresh(room)
    return room


def _extract_goals(text: str, top_n: int = 5) -> list[str]:
    words = re.findall(r"\b[a-z]{4,}\b", text.lower())
    return [word for word, _ in Counter(words).most_common(top_n)]


def _select_agents(session: Session, goals: list[str], query: str) -> list[Agent]:
    agents = list(session.exec(select(Agent).where(Agent.status.in_(["active", "draft", "ACTIVE", "DRAFT"]))))
    if not agents:
        return []

    selected: list[Agent] = []
    query_text = f"{query} {' '.join(goals)}".lower()
    for agent in agents:
        competency = f"{agent.role_description} {agent.system_prompt}".lower()
        if any(token in competency for token in query_text.split()):
            selected.append(agent)

    if not selected:
        selected = agents[:2]

    return selected[:4]


def log_step(
    session: Session,
    *,
    run_id: str,
    step_type: str,
    content: dict[str, Any] | list[Any] | str,
    sources: list[dict[str, Any]] | None = None,
) -> AgentStep:
    step = AgentStep(run_id=run_id, step_type=step_type, content_json=content)
    session.add(step)
    session.flush()

    for src in sources or []:
        session.add(
            AgentSource(
                step_id=step.id,
                source_type=src.get("source_type"),
                ref_id=src.get("ref_id"),
                snippet=src.get("snippet"),
                score=src.get("score"),
            )
        )

    session.flush()
    return step


def _render_html_from_markdown(markdown_text: str) -> str:
    lines = markdown_text.splitlines()
    html_lines: list[str] = ["<html><body>"]
    for line in lines:
        if line.startswith("# "):
            html_lines.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("- "):
            html_lines.append(f"<li>{html.escape(line[2:])}</li>")
        elif line.strip() == "":
            html_lines.append("<br/>")
        else:
            html_lines.append(f"<p>{html.escape(line)}</p>")
    html_lines.append("</body></html>")
    return "\n".join(html_lines)


def _artifact_paths(room_id: str) -> tuple[Path, Path]:
    settings = get_settings()
    reports_dir = ensure_directory(settings.reports_dir_path)
    return Path(reports_dir) / f"room_{room_id}.html", Path(reports_dir) / f"room_{room_id}.pdf"


def _report_object_keys(room_id: str) -> tuple[str, str, str]:
    settings = get_settings()
    base = f"{settings.S3_REPORTS_PREFIX}/{room_id}"
    return f"{base}/report.md", f"{base}/report.html", f"{base}/report.pdf"


def room_thread_id(room_id: str) -> str:
    return f"thread_{room_id[:12]}"


def _write_artifacts(room: Room, report_md: str) -> tuple[str, str | None]:
    html_path, pdf_path = _artifact_paths(room.id)
    md_key, html_key, pdf_key = _report_object_keys(room.id)

    html_content = _render_html_from_markdown(report_md)
    html_path.write_text(html_content, encoding="utf-8")

    try:
        s3_service.upload_text(md_key, report_md, content_type="text/markdown")
        s3_service.upload_text(html_key, html_content, content_type="text/html")
    except Exception:
        pass

    pdf_written = None
    try:
        from weasyprint import HTML  # type: ignore

        HTML(string=html_content).write_pdf(str(pdf_path))
        pdf_bytes = pdf_path.read_bytes()
        try:
            s3_service.upload_bytes(pdf_key, pdf_bytes, content_type="application/pdf")
            pdf_written = s3_service.s3_uri(pdf_key)
        except Exception:
            pdf_written = str(pdf_path)
    except Exception:
        pdf_written = None

    try:
        return s3_service.s3_uri(html_key), pdf_written
    except Exception:
        return str(html_path), pdf_written


def run_room_workflow(
    session: Session,
    room_id: str,
    document_path: str | None = None,
    context_text: str | None = None,
) -> Room:
    room = session.get(Room, room_id)
    if room is None:
        raise NotFoundError(f"Room '{room_id}' was not found.")

    room.status = "PROCESSING"

    context = context_text or room.initial_query
    if document_path:
        parsed_text, _file_type = auto_parse_document(document_path)
        context = f"{context}\n\n{parsed_text}"

    room.context_text = context

    from app.services.langgraph_workflow import run_room_langgraph

    mission_goals, final_report = run_room_langgraph(session, room, context)
    room.mission_goals_json = mission_goals
    room.final_report_md = final_report

    _write_artifacts(room, room.final_report_md)
    room.status = "COMPLETED"

    session.add(room)
    session.commit()
    session.refresh(room)
    return room


def process_room_workflow(
    room_id: str,
    document_path: str | None = None,
    context_text: str | None = None,
) -> None:
    with SessionLocal() as session:
        try:
            run_room_workflow(session, room_id, document_path, context_text)
        except Exception as exc:
            room = session.get(Room, room_id)
            if room is not None:
                room.status = "FAILED"
                room.final_report_md = (
                    "# Failed Room Run\n\n"
                    "The room workflow crashed before completion.\n\n"
                    f"Error: {str(exc)}"
                )
                session.add(room)
                session.commit()


def get_room_status(session: Session, room_id: str) -> Room:
    room = session.get(Room, room_id)
    if room is None:
        raise NotFoundError(f"Room '{room_id}' was not found.")
    return room


def get_room_trace(session: Session, room_id: str) -> dict[str, Any]:
    room = get_room_status(session, room_id)

    runs = list(session.exec(select(AgentRun).where(AgentRun.room_id == room_id).order_by(AgentRun.started_at)))
    run_payload: list[dict[str, Any]] = []

    for run in runs:
        steps = list(session.exec(select(AgentStep).where(AgentStep.run_id == run.id).order_by(AgentStep.created_at)))
        step_payload: list[dict[str, Any]] = []
        for step in steps:
            sources = list(session.exec(select(AgentSource).where(AgentSource.step_id == step.id)))
            step_payload.append(
                {
                    "id": step.id,
                    "step_type": step.step_type,
                    "content_json": step.content_json,
                    "created_at": step.created_at.isoformat(),
                    "sources": [
                        {
                            "source_type": s.source_type,
                            "ref_id": s.ref_id,
                            "document_id": s.document_id,
                            "title": s.title,
                            "snippet": s.snippet,
                            "page_number": s.page_number,
                            "score": s.score,
                        }
                        for s in sources
                    ],
                }
            )

        run_payload.append(
            {
                "id": run.id,
                "agent_id": run.agent_id,
                "status": run.status,
                "bid_reason": run.bid_reason,
                "steps": step_payload,
            }
        )

    return {"room_id": room.id, "status": room.status, "runs": run_payload}


def chat_with_room(session: Session, room_id: str, query: str) -> str:
    room = get_room_status(session, room_id)
    report = room.final_report_md or "No report generated yet."

    lowered = query.lower()
    if "goal" in lowered:
        return "Mission goals: " + ", ".join(room.mission_goals_json)
    if "trace" in lowered:
        trace = get_room_trace(session, room_id)
        return f"Trace has {len(trace['runs'])} agent runs with granular steps logged."
    if "summary" in lowered or "report" in lowered:
        return report[:1800]

    return (
        "Ask me about goals, trace, or summary. "
        "I can answer based on final report and logged reasoning history."
    )


def get_room_artifacts(room_id: str) -> tuple[str | None, str | None]:
    _md_key, html_key, pdf_key = _report_object_keys(room_id)
    try:
        html_s3 = s3_service.s3_uri(html_key) if s3_service.object_exists(html_key) else None
        pdf_s3 = s3_service.s3_uri(pdf_key) if s3_service.object_exists(pdf_key) else None
        if html_s3 or pdf_s3:
            return html_s3, pdf_s3
    except Exception:
        pass

    html_path, pdf_path = _artifact_paths(room_id)
    html_value = str(html_path) if html_path.exists() else None
    pdf_value = str(pdf_path) if pdf_path.exists() else None
    return html_value, pdf_value


def get_room_result_documents(room_id: str) -> dict[str, str | None]:
    md_key, html_key, pdf_key = _report_object_keys(room_id)

    md_uri = s3_service.s3_uri(md_key) if s3_service.object_exists(md_key) else None
    html_uri = s3_service.s3_uri(html_key) if s3_service.object_exists(html_key) else None

    pdf_exists = s3_service.object_exists(pdf_key)
    if not pdf_exists:
        room = None
        with SessionLocal() as session:
            room = session.get(Room, room_id)
            if room and room.final_report_md:
                try:
                    _write_artifacts(room, room.final_report_md)
                except Exception:
                    pass
        pdf_exists = s3_service.object_exists(pdf_key)

    pdf_uri = s3_service.s3_uri(pdf_key) if pdf_exists else None

    return {
        "report_md_s3_uri": md_uri,
        "report_html_s3_uri": html_uri,
        "report_pdf_s3_uri": pdf_uri,
        "report_md_download_url": s3_service.make_presigned_get_url(md_key) if md_uri else None,
        "report_html_download_url": s3_service.make_presigned_get_url(html_key) if html_uri else None,
        "report_pdf_download_url": s3_service.make_presigned_get_url(pdf_key) if pdf_uri else None,
    }
