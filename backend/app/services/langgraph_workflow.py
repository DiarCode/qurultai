from __future__ import annotations

from collections import Counter
from typing import Any, TypedDict

from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.utils import utc_now
from app.models.agent import Agent
from app.models.agent_run import AgentRun
from app.models.agent_source import AgentSource
from app.models.agent_step import AgentStep
from app.models.room import Room
from app.services import rag_tool_service


class RoomGraphState(TypedDict):
    session: Session
    room_id: str
    user_input: str
    context_text: str
    mission_goals: list[str]
    active_agent_ids: list[str]
    agent_fragments: list[str]
    has_conflict: bool
    critic_note: str
    round_index: int
    max_rounds: int
    final_report_md: str


def _extract_goals(text: str, top_n: int = 5) -> list[str]:
    words = [token for token in text.lower().split() if token.isalpha() and len(token) >= 4]
    return [word for word, _ in Counter(words).most_common(top_n)]


def _invoke_ollama(prompt: str, system_prompt: str | None = None) -> str:
    settings = get_settings()
    try:
        from langchain_ollama import ChatOllama

        kwargs: dict[str, Any] = {
            "model": settings.OLLAMA_MODEL,
            "base_url": settings.OLLAMA_BASE_URL,
            "temperature": settings.OLLAMA_TEMPERATURE,
        }
        client_kwargs: dict[str, Any] = {"timeout": settings.OLLAMA_TIMEOUT_SECONDS}
        # Note: Ollama handles cloud auth internally via signature-based mechanism
        # Do NOT use Bearer tokens - let Ollama sign requests automatically
        kwargs["client_kwargs"] = client_kwargs

        llm = ChatOllama(**kwargs)
        final_prompt = prompt if not system_prompt else f"System: {system_prompt}\n\nUser: {prompt}"
        response = llm.invoke(final_prompt)
        return str(getattr(response, "content", "") or "").strip()
    except Exception:
        return ""


def _log_step(
    session: Session,
    *,
    run_id: str,
    step_type: str,
    content: dict[str, Any] | list[Any] | str,
    sources: list[dict[str, Any]] | None = None,
) -> None:
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


def _preprocessor_node(state: RoomGraphState) -> RoomGraphState:
    if not state.get("context_text"):
        state["context_text"] = state["user_input"]
    return state


def _orchestrator_node(state: RoomGraphState) -> RoomGraphState:
    fallback_goals = _extract_goals(state["context_text"])
    extra_instruction = ""
    if state.get("round_index", 0) > 0:
        extra_instruction = (
            "\nPrevious specialist round had conflicts. "
            "Refine mission goals to resolve contradictions.\n"
            f"Critic note: {state.get('critic_note', '')}\n"
        )
    prompt = (
        "Break this request into 3-5 measurable mission goals. "
        "Return one bullet per line.\n\n"
        f"Request:\n{state['context_text']}"
        + extra_instruction
    )
    content = _invoke_ollama(prompt)
    goals = [line.strip().strip("-").strip() for line in content.splitlines() if line.strip()]
    state["mission_goals"] = goals[:5] if goals else fallback_goals
    return state


def _bidding_node(state: RoomGraphState) -> RoomGraphState:
    session = state["session"]
    goals_text = ", ".join(state.get("mission_goals", []))

    candidates = list(
        session.exec(select(Agent).where(Agent.status.in_(["active", "draft", "ACTIVE", "DRAFT"])))
    )
    selected_ids: list[str] = []

    for agent in candidates:
        bid_prompt = (
            f"Mission goals: {goals_text}\n"
            f"Agent role: {agent.role_description}\n"
            f"Agent prompt: {agent.system_prompt}\n\n"
            "Should this agent participate? Answer only TRUE or FALSE."
        )
        bid = _invoke_ollama(bid_prompt).upper()
        if "TRUE" in bid:
            selected_ids.append(agent.id)

    if not selected_ids:
        selected_ids = [agent.id for agent in candidates[:3]]

    state["active_agent_ids"] = selected_ids
    return state


def _specialist_node(state: RoomGraphState) -> RoomGraphState:
    session = state["session"]
    room_id = state["room_id"]
    goals = state.get("mission_goals", [])
    fragments: list[str] = []

    for agent_id in state.get("active_agent_ids", []):
        agent = session.get(Agent, agent_id)
        if agent is None:
            continue

        run = AgentRun(
            room_id=room_id,
            agent_id=agent.id,
            status="THINKING",
            bid_reason="LangGraph bidding selected this specialist",
            started_at=utc_now(),
        )
        session.add(run)
        session.flush()

        thought = _invoke_ollama(
            prompt=f"Request: {state['user_input']}\nGoals: {goals}\nWrite a concise reasoning thought.",
            system_prompt=agent.system_prompt,
        )
        if not thought:
            thought = f"I will analyze this room as {agent.name}."

        _log_step(session, run_id=run.id, step_type="THOUGHT", content={"text": thought})

        run.status = "ACTING"
        session.add(run)
        session.flush()

        _log_step(
            session,
            run_id=run.id,
            step_type="TOOL_CALL",
            content={"tool": "rag_search", "query": state["user_input"], "agent_id": agent.id},
        )

        hits = rag_tool_service.rag_search(state["user_input"], limit=5, agent_id=agent.id)
        tool_summary = {
            "result_count": len(hits),
            "top_snippets": [str(item.get("text") or "")[:220] for item in hits[:3]],
        }
        _log_step(
            session,
            run_id=run.id,
            step_type="TOOL_OUTPUT",
            content=tool_summary,
            sources=[
                {
                    "source_type": "KNOWLEDGE_BASE",
                    "ref_id": (
                        f"knowledge_document:{str(item.get('document_id') or '')}"
                        f"|s3://{get_settings().MINIO_BUCKET}/{str(item.get('s3_key') or '')}"
                    ),
                    "snippet": str(item.get("text") or "")[:220],
                    "score": float(item.get("score") or 0.0),
                }
                for item in hits
            ],
        )

        run.status = "WRITING"
        session.add(run)
        session.flush()

        fragment_prompt = (
            f"User request: {state['user_input']}\n"
            f"Goals: {goals}\n"
            f"RAG snippets: {tool_summary['top_snippets']}\n\n"
            "Write a compact markdown section with findings and recommendation."
        )
        fragment = _invoke_ollama(fragment_prompt, system_prompt=agent.system_prompt)
        if not fragment:
            fragment = (
                f"## {agent.name}\n"
                f"- Competency: {agent.role_description}\n"
                f"- Findings: aligned with goals {', '.join(goals[:3])}\n"
                "- Recommendation: include in consolidated compromise report.\n"
            )

        if not fragment.startswith("## "):
            fragment = f"## {agent.name}\n" + fragment

        _log_step(session, run_id=run.id, step_type="MD_FRAGMENT", content={"markdown": fragment})
        fragments.append(fragment)

        run.status = "DONE"
        run.finished_at = utc_now()
        session.add(run)

    state["agent_fragments"] = fragments
    return state


def _critic_node(state: RoomGraphState) -> RoomGraphState:
    prompt = (
        "Review specialist fragments and decide if they conflict. "
        "Return first line as CONFLICT: TRUE or CONFLICT: FALSE and then a short reason.\n\n"
        f"Fragments:\n{state.get('agent_fragments', [])}"
    )
    review = _invoke_ollama(prompt)
    lowered = review.lower()
    has_conflict = "conflict: true" in lowered

    if not review:
        contradiction_tokens = ["contradict", "incompatible", "cannot both"]
        has_conflict = any(token in "\n".join(state.get("agent_fragments", [])).lower() for token in contradiction_tokens)
        review = "Auto-critic fallback decision based on contradiction token scan."

    state["has_conflict"] = has_conflict
    state["critic_note"] = review[:600]
    if has_conflict:
        state["round_index"] = state.get("round_index", 0) + 1
    return state


def _route_after_critic(state: RoomGraphState) -> str:
    if state.get("has_conflict") and state.get("round_index", 0) < state.get("max_rounds", 2):
        return "orchestrator"
    return "consolidator"


def _consolidator_node(state: RoomGraphState) -> RoomGraphState:
    prompt = (
        f"Mission goals:\n{state.get('mission_goals', [])}\n\n"
        f"Specialist fragments:\n{state.get('agent_fragments', [])}\n\n"
        "Produce final markdown report with goals, tradeoffs, and critic conclusion."
    )
    report = _invoke_ollama(prompt)
    if not report:
        report = (
            "# Final Consolidated Report\n\n"
            f"Generated: {utc_now().isoformat()}\n\n"
            "## Mission Goals\n"
            + "\n".join(f"- {goal}" for goal in state.get("mission_goals", []))
            + "\n\n"
            + "\n".join(state.get("agent_fragments", []))
            + "\n\n## Critic Conclusion\n"
            + "Specialist outputs were synthesized without unresolved contradictions."
        )
    state["final_report_md"] = report
    return state


def build_room_graph() -> Any:
    from langgraph.graph import END, StateGraph

    graph = StateGraph(RoomGraphState)
    graph.add_node("preprocessor", _preprocessor_node)
    graph.add_node("orchestrator", _orchestrator_node)
    graph.add_node("bidding", _bidding_node)
    graph.add_node("specialist", _specialist_node)
    graph.add_node("critic", _critic_node)
    graph.add_node("consolidator", _consolidator_node)

    graph.set_entry_point("preprocessor")
    graph.add_edge("preprocessor", "orchestrator")
    graph.add_edge("orchestrator", "bidding")
    graph.add_edge("bidding", "specialist")
    graph.add_edge("specialist", "critic")
    graph.add_conditional_edges(
        "critic",
        _route_after_critic,
        {
            "orchestrator": "orchestrator",
            "consolidator": "consolidator",
        },
    )
    graph.add_edge("consolidator", END)
    return graph.compile()


def run_room_langgraph(session: Session, room: Room, context_text: str) -> tuple[list[str], str]:
    graph = build_room_graph()
    initial: RoomGraphState = {
        "session": session,
        "room_id": room.id,
        "user_input": room.initial_query,
        "context_text": context_text,
        "mission_goals": [],
        "active_agent_ids": [],
        "agent_fragments": [],
        "has_conflict": False,
        "critic_note": "",
        "round_index": 0,
        "max_rounds": max(1, min(get_settings().LANGGRAPH_MAX_STEPS, 4)),
        "final_report_md": "",
    }
    result = graph.invoke(initial)
    goals = list(result.get("mission_goals", []))
    report = str(result.get("final_report_md", ""))
    return goals, report


def run_graph_once(user_input: str, context_text: str | None = None) -> dict[str, Any]:
    fallback_goals = _extract_goals(context_text or user_input)
    return {
        "user_input": user_input,
        "context_text": context_text or user_input,
        "mission_goals": fallback_goals,
        "active_agent_ids": ["orchestrator_critic"],
        "agent_fragments": ["## orchestrator_critic\n- fallback smoke fragment"],
        "has_conflict": False,
        "critic_note": "",
        "round_index": 0,
        "max_rounds": 1,
        "final_report_md": "# LangGraph Smoke\n\nFallback result without room/session context.",
    }
