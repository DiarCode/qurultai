from __future__ import annotations

import argparse
import base64
import time
from uuid import uuid4

import httpx


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run end-to-end API request flow against running backend.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/api/v1", help="API base URL")
    parser.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout seconds")
    parser.add_argument("--poll-interval", type=float, default=0.2, help="Status poll interval seconds")
    parser.add_argument("--poll-attempts", type=int, default=80, help="Max polling attempts")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    suffix = uuid4().hex[:8]

    with httpx.Client(timeout=args.timeout) as client:
        # Create tool
        tool_name = f"manual_tool_{suffix}"
        r = client.post(
            f"{args.base_url}/tools",
            json={
                "name": tool_name,
                "description": "Manual request flow tool",
                "input_schema_json": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            },
        )
        r.raise_for_status()
        tool = r.json()
        tool_id = tool["id"]
        print("tool_created", tool_id, tool["name"])

        # Fetch tools
        tools = client.get(f"{args.base_url}/tools")
        tools.raise_for_status()
        print("tools_count", len(tools.json()))

        # Create agent
        agent_key = f"manual_agent_{suffix}"
        r = client.post(
            f"{args.base_url}/agents",
            json={
                "key": agent_key,
                "name": "Manual Request Specialist",
                "role_description": "legal and financial specialist",
                "system_prompt": "Analyze and provide concise recommendations.",
                "status": "active",
                "tool_ids": [tool_id],
            },
        )
        r.raise_for_status()
        agent = r.json()
        agent_id = agent["id"]
        print("agent_created", agent_id, agent["key"])

        # Upload a small knowledge document for this agent
        kb_text = (
            "Municipal transport proposal baseline:\n"
            "Estimated capex 10M, expected ROI in 4 years, and legal constraint on procurement timeline."
        )
        kb_payload = {
            "source_filename": f"seed_{suffix}.txt",
            "mime_type": "text/plain",
            "content_base64": base64.b64encode(kb_text.encode("utf-8")).decode("utf-8"),
            "agent_id": agent_id,
            "title": "Municipal transport baseline",
        }
        k = client.post(f"{args.base_url}/knowledge/documents/upload", json=kb_payload)
        k.raise_for_status()
        print("knowledge_uploaded", k.json()["document"]["id"], "chunks", k.json()["chunks_ingested"])

        # Fetch agents
        agents = client.get(f"{args.base_url}/agents")
        agents.raise_for_status()
        print("agents_count", len(agents.json()))

        # Start room workflow
        r = client.post(
            f"{args.base_url}/rooms/create",
            json={
                "query": "Assess legal and financial viability of municipal infrastructure proposal",
                "async_mode": True,
            },
        )
        r.raise_for_status()
        room = r.json()
        room_id = room["room_id"]
        print("room_created", room_id, room["status"])

        # Poll status
        status = room["status"]
        for _ in range(args.poll_attempts):
            s = client.get(f"{args.base_url}/rooms/{room_id}/status")
            s.raise_for_status()
            status = s.json()["status"]
            if status in {"COMPLETED", "FAILED"}:
                break
            time.sleep(args.poll_interval)
        print("room_status", status)

        if status != "COMPLETED":
            raise RuntimeError(f"Room did not complete successfully: {status}")

        # Fetch outputs
        report = client.get(f"{args.base_url}/rooms/{room_id}/report")
        report.raise_for_status()
        report_payload = report.json()
        print("report_thread", report_payload.get("thread_id"))
        print("report_len", len(report_payload.get("report_md") or ""))

        trace = client.get(f"{args.base_url}/rooms/{room_id}/trace")
        trace.raise_for_status()
        print("trace_runs", len(trace.json().get("runs", [])))

        # Continue conversation with orchestrator-style prompt
        chat = client.post(
            f"{args.base_url}/rooms/chat",
            json={
                "room_id": room_id,
                "query": "As orchestrator, summarize goals, tradeoffs, and final recommendation.",
            },
        )
        chat.raise_for_status()
        print("chat_answer", (chat.json().get("answer") or "")[:300])


if __name__ == "__main__":
    main()
