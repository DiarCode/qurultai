from __future__ import annotations

from time import sleep
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_tools_crud_and_async_room_flow() -> None:
    suffix = uuid4().hex[:8]

    tool_name = f"tool_{suffix}"
    tool_response = client.post(
        "/api/v1/tools",
        json={
            "name": tool_name,
            "description": "Test tool",
            "input_schema_json": {"type": "object", "properties": {"query": {"type": "string"}}},
        },
    )
    assert tool_response.status_code == 201
    tool_id = tool_response.json()["id"]

    updated_tool = client.patch(
        f"/api/v1/tools/{tool_id}",
        json={"description": "Updated test tool"},
    )
    assert updated_tool.status_code == 200
    assert updated_tool.json()["description"] == "Updated test tool"

    agent_key = f"agent_{suffix}"
    agent_response = client.post(
        "/api/v1/agents",
        json={
            "key": agent_key,
            "name": "Async Flow Agent",
            "role_description": "legal and financial specialist",
            "system_prompt": "Analyze and summarize.",
            "status": "active",
            "tool_ids": [tool_id],
        },
    )
    assert agent_response.status_code == 201

    room_response = client.post(
        "/api/v1/rooms/create",
        json={"query": "Need legal and financial overview", "async_mode": True},
    )
    assert room_response.status_code == 200
    room_payload = room_response.json()
    assert room_payload["status"] == "PROCESSING"

    room_id = room_payload["room_id"]
    status = "PROCESSING"
    for _ in range(40):
        status_response = client.get(f"/api/v1/rooms/{room_id}/status")
        assert status_response.status_code == 200
        status = status_response.json()["status"]
        if status in {"COMPLETED", "FAILED"}:
            break
        sleep(0.05)

    assert status == "COMPLETED"

    report_response = client.get(f"/api/v1/rooms/{room_id}/report")
    assert report_response.status_code == 200
    report_payload = report_response.json()
    assert report_payload["report_md"]
    assert report_payload["thread_id"]

    trace_response = client.get(f"/api/v1/rooms/{room_id}/trace")
    assert trace_response.status_code == 200
    assert len(trace_response.json()["runs"]) >= 1
