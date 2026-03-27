from __future__ import annotations

from time import sleep
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_requests_agent_tool_room_and_chat_flow() -> None:
    suffix = uuid4().hex[:8]

    # 1) Create tool
    tool_name = f"req_tool_{suffix}"
    create_tool = client.post(
        "/api/v1/tools",
        json={
            "name": tool_name,
            "description": "Request flow tool",
            "input_schema_json": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
            "endpoint_url": None,
        },
    )
    assert create_tool.status_code == 201
    tool_id = create_tool.json()["id"]

    # 2) Fetch tool list and validate created tool exists
    all_tools = client.get("/api/v1/tools")
    assert all_tools.status_code == 200
    assert any(item["id"] == tool_id for item in all_tools.json())

    # 3) Create agent with this tool
    agent_key = f"req_agent_{suffix}"
    create_agent = client.post(
        "/api/v1/agents",
        json={
            "key": agent_key,
            "name": "Request Flow Specialist",
            "role_description": "orchestrator companion for legal and financial analysis",
            "system_prompt": "Analyze room context and provide concise specialist findings.",
            "status": "active",
            "tool_ids": [tool_id],
        },
    )
    assert create_agent.status_code == 201
    agent_id = create_agent.json()["id"]

    # 4) Fetch agents and validate created agent exists
    all_agents = client.get("/api/v1/agents")
    assert all_agents.status_code == 200
    assert any(item["id"] == agent_id for item in all_agents.json())

    # 5) Start workflow (async) via room creation
    create_room = client.post(
        "/api/v1/rooms/create",
        json={
            "query": "Assess legal and financial viability of municipal infrastructure proposal",
            "async_mode": True,
        },
    )
    assert create_room.status_code == 200
    room_payload = create_room.json()
    room_id = room_payload["room_id"]
    assert room_payload["status"] in {"PROCESSING", "COMPLETED"}

    # 6) Poll room status until completed
    status = "PROCESSING"
    mission_goals: list[str] = []
    for _ in range(80):
        check = client.get(f"/api/v1/rooms/{room_id}/status")
        assert check.status_code == 200
        body = check.json()
        status = body["status"]
        mission_goals = body.get("mission_goals", [])
        if status in {"COMPLETED", "FAILED"}:
            break
        sleep(0.05)

    assert status == "COMPLETED"
    assert isinstance(mission_goals, list)

    # 7) Fetch output report + trace
    report = client.get(f"/api/v1/rooms/{room_id}/report")
    assert report.status_code == 200
    report_payload = report.json()
    assert report_payload["report_md"]
    assert report_payload["thread_id"]

    trace = client.get(f"/api/v1/rooms/{room_id}/trace")
    assert trace.status_code == 200
    runs = trace.json()["runs"]
    assert len(runs) >= 1

    # 8) Continue agentic conversation (ask orchestrator-oriented question)
    chat = client.post(
        "/api/v1/rooms/chat",
        json={
            "room_id": room_id,
            "query": "As orchestrator, summarize mission goals and highlight contradictions if any.",
        },
    )
    assert chat.status_code == 200
    answer = chat.json()["answer"]
    assert isinstance(answer, str)
    assert len(answer.strip()) > 0
