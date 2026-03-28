from __future__ import annotations

import argparse
import base64
import sys
import time
from dataclasses import dataclass, field
from uuid import uuid4

import httpx


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str = ""


@dataclass
class RunState:
    checks: list[CheckResult] = field(default_factory=list)

    def add(self, name: str, ok: bool, detail: str = "") -> None:
        self.checks.append(CheckResult(name=name, ok=ok, detail=detail))
        status = "PASS" if ok else "FAIL"
        suffix = f" | {detail}" if detail else ""
        print(f"[{status}] {name}{suffix}")

    @property
    def failed(self) -> list[CheckResult]:
        return [item for item in self.checks if not item.ok]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Live integration test for all backend endpoints.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/api/v1", help="Base API URL")
    parser.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout")
    parser.add_argument("--poll-attempts", type=int, default=240, help="Workflow status polling attempts")
    parser.add_argument("--poll-interval", type=float, default=0.5, help="Workflow status polling interval")
    return parser.parse_args()


def _safe_call(state: RunState, name: str, fn):
    try:
        value = fn()
        state.add(name, True)
        return value
    except Exception as exc:  # noqa: BLE001
        state.add(name, False, str(exc))
        return None


def _expect_status(response: httpx.Response, expected: int) -> None:
    if response.status_code != expected:
        raise RuntimeError(f"expected {expected}, got {response.status_code}, body={response.text[:500]}")


def main() -> int:
    args = parse_args()
    state = RunState()
    suffix = uuid4().hex[:8]

    tool_id = None
    agent_id = None
    document_id = None
    room_id = None

    with httpx.Client(timeout=args.timeout) as client:
        # Health
        def check_health():
            res = client.get(f"{args.base_url}/health")
            _expect_status(res, 200)
            payload = res.json()
            if payload.get("status") != "ok":
                raise RuntimeError(f"unexpected health status: {payload}")

        _safe_call(state, "health", check_health)

        # Tool CRUD
        def create_tool():
            nonlocal tool_id
            res = client.post(
                f"{args.base_url}/tools",
                json={
                    "name": f"e2e_tool_{suffix}",
                    "description": "e2e tool",
                    "input_schema_json": {"type": "object", "properties": {"query": {"type": "string"}}},
                },
            )
            _expect_status(res, 201)
            tool_id = res.json()["id"]

        _safe_call(state, "tools.create", create_tool)

        def list_tools():
            res = client.get(f"{args.base_url}/tools")
            _expect_status(res, 200)
            if tool_id and not any(item["id"] == tool_id for item in res.json()):
                raise RuntimeError("created tool not found in list")

        _safe_call(state, "tools.list", list_tools)

        def get_tool():
            if not tool_id:
                raise RuntimeError("tool_id is missing")
            res = client.get(f"{args.base_url}/tools/{tool_id}")
            _expect_status(res, 200)

        _safe_call(state, "tools.get", get_tool)

        def update_tool():
            if not tool_id:
                raise RuntimeError("tool_id is missing")
            res = client.patch(f"{args.base_url}/tools/{tool_id}", json={"description": "e2e tool updated"})
            _expect_status(res, 200)

        _safe_call(state, "tools.update", update_tool)

        # Agent CRUD
        def create_agent():
            nonlocal agent_id
            if not tool_id:
                raise RuntimeError("tool_id is missing")
            res = client.post(
                f"{args.base_url}/agents",
                json={
                    "key": f"e2e_agent_{suffix}",
                    "name": "E2E Agent",
                    "role_description": "legal and financial specialist",
                    "system_prompt": "Analyze and summarize.",
                    "status": "active",
                    "tool_ids": [tool_id],
                },
            )
            _expect_status(res, 201)
            agent_id = res.json()["id"]

        _safe_call(state, "agents.create", create_agent)

        def list_agents():
            res = client.get(f"{args.base_url}/agents")
            _expect_status(res, 200)
            if agent_id and not any(item["id"] == agent_id for item in res.json()):
                raise RuntimeError("created agent not found in list")

        _safe_call(state, "agents.list", list_agents)

        def get_agent():
            if not agent_id:
                raise RuntimeError("agent_id is missing")
            res = client.get(f"{args.base_url}/agents/{agent_id}")
            _expect_status(res, 200)

        _safe_call(state, "agents.get", get_agent)

        def update_agent():
            if not agent_id:
                raise RuntimeError("agent_id is missing")
            res = client.patch(f"{args.base_url}/agents/{agent_id}", json={"name": "E2E Agent Updated"})
            _expect_status(res, 200)

        _safe_call(state, "agents.update", update_agent)

        def list_agent_tools():
            if not agent_id:
                raise RuntimeError("agent_id is missing")
            res = client.get(f"{args.base_url}/agents/{agent_id}/tools")
            _expect_status(res, 200)

        _safe_call(state, "agents.tools.list", list_agent_tools)

        # Agent documents CRUD + knowledge upload/search/download
        def upload_knowledge_document():
            nonlocal document_id
            payload = {
                "source_filename": f"e2e_{suffix}.txt",
                "mime_type": "text/plain",
                "content_base64": base64.b64encode(
                    b"Transport policy baseline: ROI in 4 years, procurement legal risk, budget 10M."
                ).decode("utf-8"),
                "agent_id": agent_id,
                "title": "E2E Knowledge",
            }
            res = client.post(f"{args.base_url}/knowledge/documents/upload", json=payload)
            _expect_status(res, 201)
            document_id = res.json()["document"]["id"]

        _safe_call(state, "knowledge.upload", upload_knowledge_document)

        def list_knowledge_documents():
            res = client.get(f"{args.base_url}/knowledge/documents")
            _expect_status(res, 200)
            if document_id and not any(item["id"] == document_id for item in res.json().get("items", [])):
                raise RuntimeError("uploaded document not in list")

        _safe_call(state, "knowledge.list", list_knowledge_documents)

        def list_agent_documents():
            if not agent_id:
                raise RuntimeError("agent_id is missing")
            res = client.get(f"{args.base_url}/agents/{agent_id}/documents")
            _expect_status(res, 200)

        _safe_call(state, "agents.documents.list", list_agent_documents)

        def search_knowledge():
            res = client.post(
                f"{args.base_url}/knowledge/search",
                json={"query": "procurement legal risk", "limit": 5, "agent_id": agent_id},
            )
            _expect_status(res, 200)
            items = res.json().get("items", [])
            if not isinstance(items, list):
                raise RuntimeError("search response invalid")

        _safe_call(state, "knowledge.search", search_knowledge)

        def download_knowledge():
            if not document_id:
                raise RuntimeError("document_id is missing")
            res = client.get(f"{args.base_url}/knowledge/documents/{document_id}/download")
            _expect_status(res, 200)
            payload = res.json()
            if not payload.get("s3_uri"):
                raise RuntimeError("s3_uri missing")

        _safe_call(state, "knowledge.download-meta", download_knowledge)

        # Workflow start/status/report/trace/chat/result-documents
        def start_room_workflow():
            nonlocal room_id
            res = client.post(
                f"{args.base_url}/rooms/create",
                json={
                    "query": "Assess legal and financial viability of municipal transport proposal",
                    "context_text": "Budget is 10M, legal procurement window is strict.",
                    "async_mode": True,
                },
            )
            _expect_status(res, 200)
            room_id = res.json()["room_id"]

        _safe_call(state, "rooms.create", start_room_workflow)

        def await_room_completion():
            if not room_id:
                raise RuntimeError("room_id is missing")
            last_status = None
            for _ in range(args.poll_attempts):
                res = client.get(f"{args.base_url}/rooms/{room_id}/status")
                _expect_status(res, 200)
                payload = res.json()
                last_status = payload.get("status")
                if last_status in {"COMPLETED", "FAILED"}:
                    break
                time.sleep(args.poll_interval)
            if last_status != "COMPLETED":
                raise RuntimeError(f"workflow did not complete successfully (status={last_status})")

        _safe_call(state, "rooms.await-completed", await_room_completion)

        def room_report():
            if not room_id:
                raise RuntimeError("room_id is missing")
            res = client.get(f"{args.base_url}/rooms/{room_id}/report")
            _expect_status(res, 200)
            if not (res.json().get("report_md") or "").strip():
                raise RuntimeError("empty report")

        _safe_call(state, "rooms.report", room_report)

        def room_trace():
            if not room_id:
                raise RuntimeError("room_id is missing")
            res = client.get(f"{args.base_url}/rooms/{room_id}/trace")
            _expect_status(res, 200)
            runs = res.json().get("runs", [])
            if not isinstance(runs, list):
                raise RuntimeError("trace payload invalid")

        _safe_call(state, "rooms.trace", room_trace)

        def room_chat():
            if not room_id:
                raise RuntimeError("room_id is missing")
            res = client.post(
                f"{args.base_url}/rooms/chat",
                json={"room_id": room_id, "query": "Summarize goals and conflicts."},
            )
            _expect_status(res, 200)
            answer = (res.json().get("answer") or "").strip()
            if not answer:
                raise RuntimeError("empty chat answer")

        _safe_call(state, "rooms.chat", room_chat)

        def room_result_documents():
            if not room_id:
                raise RuntimeError("room_id is missing")
            res = client.get(f"{args.base_url}/rooms/{room_id}/result-documents")
            _expect_status(res, 200)
            payload = res.json()
            if not payload.get("report_md_s3_uri"):
                raise RuntimeError("missing report_md_s3_uri")

        _safe_call(state, "rooms.result-documents", room_result_documents)

        # Agent doc unlink/link and cleanup CRUD tails
        def unlink_doc():
            if not (agent_id and document_id):
                raise RuntimeError("agent_id/document_id missing")
            res = client.delete(f"{args.base_url}/agents/{agent_id}/documents/{document_id}")
            _expect_status(res, 200)

        _safe_call(state, "agents.documents.unlink", unlink_doc)

        def relink_doc():
            if not (agent_id and document_id):
                raise RuntimeError("agent_id/document_id missing")
            res = client.post(f"{args.base_url}/agents/{agent_id}/documents/{document_id}")
            _expect_status(res, 200)

        _safe_call(state, "agents.documents.link", relink_doc)

        def delete_doc():
            if not document_id:
                raise RuntimeError("document_id missing")
            res = client.delete(f"{args.base_url}/knowledge/documents/{document_id}")
            _expect_status(res, 204)

        _safe_call(state, "knowledge.delete", delete_doc)

        def remove_agent_tool():
            if not (agent_id and tool_id):
                raise RuntimeError("agent_id/tool_id missing")
            res = client.delete(f"{args.base_url}/agents/{agent_id}/tools/{tool_id}")
            _expect_status(res, 200)

        _safe_call(state, "agents.tools.remove", remove_agent_tool)

        def add_agent_tool():
            if not (agent_id and tool_id):
                raise RuntimeError("agent_id/tool_id missing")
            res = client.post(f"{args.base_url}/agents/{agent_id}/tools/{tool_id}")
            _expect_status(res, 200)

        _safe_call(state, "agents.tools.add", add_agent_tool)

        def delete_agent():
            if not agent_id:
                raise RuntimeError("agent_id missing")
            res = client.delete(f"{args.base_url}/agents/{agent_id}")
            _expect_status(res, 204)

        _safe_call(state, "agents.delete", delete_agent)

        def delete_tool():
            if not tool_id:
                raise RuntimeError("tool_id missing")
            res = client.delete(f"{args.base_url}/tools/{tool_id}")
            _expect_status(res, 204)

        _safe_call(state, "tools.delete", delete_tool)

    print("\nSummary")
    print(f"checks={len(state.checks)} failed={len(state.failed)}")
    for item in state.failed:
        print(f" - {item.name}: {item.detail}")

    return 1 if state.failed else 0


if __name__ == "__main__":
    sys.exit(main())
