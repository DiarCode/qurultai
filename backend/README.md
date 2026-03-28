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

`docker-compose.yml` includes tools only:
- qdrant
- minio (S3-compatible)

Start everything:

```bash
docker compose up -d
```

Run backend separately:

```bash
uv sync
uv run uvicorn app.main:app --reload
```

OpenAI configuration (in `.env`):

```bash
OPENAI_API_KEY=<your key>
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

Useful endpoints:
- Backend: `http://127.0.0.1:8000`
- Qdrant: `http://127.0.0.1:6333`
- MinIO API: `http://127.0.0.1:9000`
- MinIO Console: `http://127.0.0.1:9001`
