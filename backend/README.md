# GovOrchestrator AI Backend

Local-first FastAPI backend foundation for GovOrchestrator AI.

## Developer commands

```bash
uv run python -m scripts.init_db
uv run uvicorn app.main:app --reload
uv run pytest
uv run ruff check .
```

## LangGraph minimal setup

- Graph scaffold: `app/services/langgraph_workflow.py`
- Optional integrations config: `app/core/integrations.py`

Run a local smoke check:

```bash
uv run python -m scripts.run_langgraph_smoke
```

Enable LangGraph-driven room execution in `.env`:

```bash
ENABLE_LANGGRAPH=true
```

Knowledge upload endpoint (JSON base64):

```bash
POST /api/v1/knowledge/documents/upload
{
	"source_filename": "doc.txt",
	"mime_type": "text/plain",
	"content_base64": "<base64>",
	"agent_id": "<optional-agent-id>",
	"title": "optional title"
}
```

## Docker local stack

`docker-compose.yml` includes:
- backend (FastAPI)
- qdrant
- ollama
- minio (S3-compatible)

Start everything:

```bash
docker compose up --build
```

Pull model for Ollama (inside container):

```bash
docker exec -it qurultai-ollama ollama pull qwen2.5:7b
```

Useful endpoints:
- Backend: `http://127.0.0.1:8000`
- Qdrant: `http://127.0.0.1:6333`
- Ollama: `http://127.0.0.1:11434`
- MinIO API: `http://127.0.0.1:9000`
- MinIO Console: `http://127.0.0.1:9001`
