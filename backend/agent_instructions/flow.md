# 🏗️ Technical Specification: Orchestrated Multi-Agent Room

## 1. System Overview
System for collaborative document analysis and report generation using **FastAPI** and **LangGraph**.
**Key Concept:** A "Room" where specialized agents (from a DB) self-select to join a task, execute tools with granular logging, and produce a consolidated MD/PDF report.

---

## 2. Core Data Models (The "Miro" Schema)

### 2.1 Agent & Tools (Database)
* **Agent**: `id, name, role_description, system_prompt, tool_permissions[]`.
* **Tool**: `id, name, description, schema (JSON), endpoint_url`.

### 2.2 Granular Logging (The "Thinking" Trace)
Instead of flat messages, use a hierarchical structure:

```typescript
interface AgentRun {
  runId: UUID;          // Unique ID for this agent's participation
  agentId: string;      // Specialist ID
  status: "THINKING" | "ACTING" | "WRITING" | "DONE";
  steps: AgentStep[];   // The granular trace
}

interface AgentStep {
  stepId: UUID;
  timestamp: DateTime;
  type: "THOUGHT" | "TOOL_CALL" | "TOOL_OUTPUT" | "MD_FRAGMENT";
  content: string | JSON; // Chain of Thought or Tool Data
  sources: {
    docId: string, 
    snippet: string, 
    score: float 
  }[];
}
```

---

## 3. LangGraph Workflow Definition

### State Definition
```python
class RoomState(TypedDict):
    user_input: str
    context_text: str           # Extracted from PDF/OCR
    mission_goals: List[str]    # Set by Orchestrator
    active_agents: List[str]    # List of Agent IDs who accepted the bid
    agent_runs: Dict[str, AgentRun] # Full trace of each agent
    final_report_md: str
```

### Nodes Logic
1.  **`preprocessor_node`**:
    * Check `user_input`. If file/image -> Use PDF library or OCR.
    * Output: `context_text`.
2.  **`orchestrator_node` (The Critic)**:
    * Analyze `context_text`.
    * Output: `mission_goals` (e.g., ["Verify Tax Compliance", "Estimate ROI"]).
3.  **`bidding_node`**:
    * Iterate all agents in DB.
    * For each: Prompt LLM: *"Given goals X, do your tools/role Y fit? (True/False)"*.
    * Output: `active_agents`.
4.  **`specialist_node` (Dynamic Map-Reduce)**:
    * **Trigger**: Parallel execution for each ID in `active_agents`.
    * **Process**: 
        * Init Agent with `system_prompt` + `tools`.
        * Loop: `THOUGHT` -> `TOOL_CALL` -> `TOOL_OUTPUT`.
        * **CRITICAL**: Every loop iteration MUST call `logStep()` to the DB.
    * Final Output: MD Fragment.
5.  **`consolidator_node`**:
    * Collect all MD fragments.
    * Critic-check for contradictions.
    * Generate `.pdf` and `.html` via `WeasyPrint` or `Pandoc`.

---

## 4. Implementation Requirements

### 4.1 Log Management Method: `logStep`
```python
def log_step(run_id: UUID, step_type: str, content: Any, sources: list):
    """
    Writes a granular step to the SQL database.
    Ensures 'History of Thought' is reconstructible for the UI.
    """
    # 1. Insert into 'agent_steps' table
    # 2. If step_type == 'TOOL_OUTPUT', optionally index in Vector DB for 'Insights'
```

### 4.2 Room Management Class
Create a `RoomManager` class to encapsulate FastAPI background tasks.
* `create_room()`: Initialize state and ID.
* `get_room_trace(room_id)`: Fetch all `AgentRun` and `AgentStep` for the UI "Thinking View".
* `chat_with_room(room_id, query)`: A dedicated agent that reads the `final_report` and the `agent_steps` to answer deep questions.

---

## 5. Final Output Architecture
The final result is not a string, but an **Artifact Bundle**:
1.  **Final Report**: `report.pdf`, `report.md`.
2.  **Audit Log**: A JSON/HTML file showing the "History of Reasoning" (all `AgentSteps`).
3.  **Active Session**: A `thread_id` for continued chat.

---

## 6. Prompting Strategy
* **Orchestrator**: Focus on decomposition. "Break this request into 3-5 measurable goals."
* **Specialist**: Focus on tool discipline. "You must think before you act. Log your thoughts clearly."
* **Critic**: Focus on synthesis. "Ensure Agent A and Agent B do not provide conflicting data."
