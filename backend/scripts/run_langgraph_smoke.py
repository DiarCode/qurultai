from __future__ import annotations

from app.services.langgraph_workflow import run_graph_once


def main() -> None:
    result = run_graph_once("Assess legal and financial viability for municipal transport program")
    print("goals", result.get("mission_goals", []))
    print("agents", result.get("active_agents", []))
    print("report_len", len(result.get("final_report_md", "")))


if __name__ == "__main__":
    main()
