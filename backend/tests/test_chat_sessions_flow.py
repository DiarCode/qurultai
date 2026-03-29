from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.services import chat_service

client = TestClient(app)


def _drain_run(run_id: str) -> list[dict]:
    events: list[dict] = []
    with client.websocket_connect(f"/api/v1/chat/runs/{run_id}/events/ws") as websocket:
        for _ in range(200):
            payload = websocket.receive_json()
            if payload["event_type"] == "connection_ready":
                continue
            events.append(payload)
            if payload["event_type"] in {"run_completed", "run_failed"}:
                break
    return events


def test_chat_sessions_continuity_and_history() -> None:
    created = client.post("/api/v1/chat/sessions", json={"title": "Continuity check"})
    assert created.status_code == 201
    session_id = created.json()["session"]["id"]

    first_message = client.post(
        f"/api/v1/chat/sessions/{session_id}/messages",
        data={"content": "What is the practical difference between a budget note and a risk note?"},
    )
    assert first_message.status_code == 201
    first_payload = first_message.json()
    first_run_id = first_payload["run"]["id"]
    assert first_payload["run"]["mode"] == "direct_answer"

    first_events = _drain_run(first_run_id)
    assert any(event["event_type"] == "assistant_message_delta" for event in first_events)
    assert any(event["event_type"] == "assistant_message_completed" for event in first_events)

    second_message = client.post(
        f"/api/v1/chat/sessions/{session_id}/messages",
        data={"content": "Continue this same chat and turn that into three concise bullet points."},
    )
    assert second_message.status_code == 201
    second_payload = second_message.json()
    second_run_id = second_payload["run"]["id"]
    _drain_run(second_run_id)

    loaded = client.get(f"/api/v1/chat/sessions/{session_id}")
    assert loaded.status_code == 200
    loaded_payload = loaded.json()
    assert len(loaded_payload["messages"]) >= 4
    assert loaded_payload["messages"][0]["role"] == "user"
    assert loaded_payload["messages"][-1]["role"] == "assistant"

    history = client.get("/api/v1/chat/sessions")
    assert history.status_code == 200
    assert any(item["id"] == session_id for item in history.json()["items"])


def test_chat_document_and_council_flow() -> None:
    created = client.post("/api/v1/chat/sessions", json={"title": "Council check"})
    assert created.status_code == 201
    session_id = created.json()["session"]["id"]

    response = client.post(
        f"/api/v1/chat/sessions/{session_id}/messages",
        data={
            "content": "Assess the legal, budget, and environmental risks in the attached memo and give a phased recommendation."
        },
        files=[
            (
                "files",
                (
                    "memo.txt",
                    b"Memo: procurement approval depends on budget clearance, environmental permit sequencing, and legal review milestones.",
                    "text/plain",
                ),
            )
        ],
    )
    assert response.status_code == 201
    payload = response.json()
    run_id = payload["run"]["id"]
    assert payload["run"]["mode"] == "council"

    events = _drain_run(run_id)
    assert any(event["event_type"] == "assistant_message_delta" for event in events)
    assert any(event["event_type"] == "retrieval_completed" for event in events)
    assert any(event["event_type"] == "agent_message_final" for event in events)
    assert any(event["event_type"] == "tool_result" for event in events)
    assert any(event["event_type"] == "report_ready" for event in events)

    loaded = client.get(f"/api/v1/chat/sessions/{session_id}")
    assert loaded.status_code == 200
    loaded_payload = loaded.json()
    assistant_messages = [
        item for item in loaded_payload["messages"] if item["role"] == "assistant"
    ]
    assert assistant_messages
    final_message = assistant_messages[-1]
    assert final_message["html_content"]
    assert final_message["actions"]
    assert len(final_message["citations"]) >= 1

    citation_keys = {
        (citation["document_id"], citation.get("location"), citation.get("snippet"))
        for citation in final_message["citations"]
    }
    assert len(citation_keys) == len(final_message["citations"])

    report_response = client.get(f"/api/v1/chat/runs/{run_id}/report/download?format=markdown")
    assert report_response.status_code == 200
    assert "# Qurultai Report" in report_response.text

    report_html_response = client.get(f"/api/v1/chat/runs/{run_id}/report/download?format=html")
    assert report_html_response.status_code == 200
    assert "Qurultai Professional Report" in report_html_response.text

    report_pdf_response = client.get(f"/api/v1/chat/runs/{run_id}/report/download?format=pdf")
    assert report_pdf_response.status_code == 200
    assert report_pdf_response.headers["content-type"] == "application/pdf"


def test_large_public_program_routes_beyond_direct_mode() -> None:
    created = client.post("/api/v1/chat/sessions", json={"title": "Kazakhstan rollout check"})
    assert created.status_code == 201
    session_id = created.json()["session"]["id"]

    response = client.post(
        f"/api/v1/chat/sessions/{session_id}/messages",
        data={
            "content": "Мне надо построить 100 школ. Проанализируй с разных сторон, насколько это сложно для Казахстана."
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["run"]["mode"] in {"specialist_assist", "council"}
    assert len(payload["run"]["selected_agents"]) >= 1


def test_user_can_force_chat_mode() -> None:
    created = client.post("/api/v1/chat/sessions", json={"title": "Manual mode check"})
    assert created.status_code == 201
    session_id = created.json()["session"]["id"]

    direct_response = client.post(
        f"/api/v1/chat/sessions/{session_id}/messages",
        data={
            "content": "Analyze this in a very simple way.",
            "mode_preference": "direct_answer",
        },
    )
    assert direct_response.status_code == 201
    direct_payload = direct_response.json()
    assert direct_payload["run"]["mode"] == "direct_answer"
    assert direct_payload["run"]["selected_agents"] == []

    council_response = client.post(
        f"/api/v1/chat/sessions/{session_id}/messages",
        data={
            "content": "Give me a broader multi-institution review of school construction delivery risks.",
            "mode_preference": "council",
        },
    )
    assert council_response.status_code == 201
    council_payload = council_response.json()
    assert council_payload["run"]["mode"] == "council"
    assert len(council_payload["run"]["selected_agents"]) >= 1


def test_output_budget_scales_by_mode() -> None:
    direct_budget = chat_service._mode_output_budget(
        mode="direct_answer",
        question="Give me a short answer.",
        docs_present=False,
        participant_count=0,
    )
    council_budget = chat_service._mode_output_budget(
        mode="council",
        question="Мне нужно межведомственно оценить строительство 100 школ, бюджет, сроки, риски и механизмы парламентского контроля.",
        docs_present=True,
        participant_count=4,
    )
    assert direct_budget < council_budget
    assert direct_budget <= 500
    assert council_budget >= 1000
