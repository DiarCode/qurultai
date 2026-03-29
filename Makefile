SHELL := /bin/bash
.DEFAULT_GOAL := help

BACKEND_DIR := backend
FRONTEND_DIR := frontend

BACKEND_HOST ?= 127.0.0.1
BACKEND_PORT ?= 8000
FRONTEND_HOST ?= 127.0.0.1
FRONTEND_PORT ?= 5173

ENABLE_LLM_CALLS ?= true
LLM_PROVIDER ?= openai
OPENAI_MODEL ?= gpt-5.4-mini
OPENAI_TIMEOUT_SECONDS ?= 30
DEBUG ?= false

.PHONY: help install backend-install frontend-install backend frontend run stop \
	test test-backend test-frontend verify llm-health smoke-openai format \
	lint lint-backend lint-frontend format-backend format-frontend \
	build build-frontend type-check-backend reset-kz-agents

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: backend-install frontend-install ## Install backend and frontend dependencies

backend-install: ## Install backend dependencies with uv
	cd $(BACKEND_DIR) && uv sync

frontend-install: ## Install frontend dependencies with bun
	cd $(FRONTEND_DIR) && bun install

backend: ## Run the FastAPI backend
	cd $(BACKEND_DIR) && \
	ENABLE_LLM_CALLS=$(ENABLE_LLM_CALLS) \
	LLM_PROVIDER=$(LLM_PROVIDER) \
	OPENAI_MODEL=$(OPENAI_MODEL) \
	OPENAI_TIMEOUT_SECONDS=$(OPENAI_TIMEOUT_SECONDS) \
	uv run uvicorn app.main:app --host $(BACKEND_HOST) --port $(BACKEND_PORT)

frontend: ## Run the Vue frontend
	cd $(FRONTEND_DIR) && bun run dev --host $(FRONTEND_HOST) --port $(FRONTEND_PORT)

run: ## Run backend and frontend together and stop both on Ctrl+C
	@set -euo pipefail; \
	trap 'kill 0' EXIT INT TERM; \
	$(MAKE) backend & \
	$(MAKE) frontend & \
	wait

stop: ## Stop local backend/frontend dev servers started on default ports
	-pkill -f "uvicorn app.main:app --host $(BACKEND_HOST) --port $(BACKEND_PORT)" || true
	-pkill -f "vite --host $(FRONTEND_HOST) --port $(FRONTEND_PORT)" || true

lint: lint-backend lint-frontend ## Run backend and frontend lint checks

lint-backend: ## Run backend Ruff lint checks
	cd $(BACKEND_DIR) && uv run ruff check .

lint-frontend: ## Run frontend lint checks
	cd $(FRONTEND_DIR) && bun run lint

test: test-backend test-frontend ## Run backend tests and frontend type-check

test-backend: ## Run backend pytest suite
	cd $(BACKEND_DIR) && DEBUG=$(DEBUG) uv run pytest

test-frontend: ## Run frontend type-check
	cd $(FRONTEND_DIR) && bun run type-check

type-check-backend: ## Run backend mypy checks
	cd $(BACKEND_DIR) && uv run mypy app

build: build-frontend ## Run production build targets

build-frontend: ## Build the frontend for production
	cd $(FRONTEND_DIR) && bun run build

verify: ## Run end-to-end verification script against running local servers
	cd $(FRONTEND_DIR) && bun scripts/verify-chat-e2e.mjs

llm-health: ## Check the configured LLM provider health
	cd $(BACKEND_DIR) && \
	ENABLE_LLM_CALLS=$(ENABLE_LLM_CALLS) \
	LLM_PROVIDER=$(LLM_PROVIDER) \
	OPENAI_MODEL=$(OPENAI_MODEL) \
	OPENAI_TIMEOUT_SECONDS=$(OPENAI_TIMEOUT_SECONDS) \
	uv run python -c "from app.services.llm_service import check_llm_health; print(check_llm_health())"

smoke-openai: ## Run a real OpenAI text + structured-output smoke test
	cd $(BACKEND_DIR) && \
	ENABLE_LLM_CALLS=$(ENABLE_LLM_CALLS) \
	LLM_PROVIDER=$(LLM_PROVIDER) \
	OPENAI_MODEL=$(OPENAI_MODEL) \
	OPENAI_TIMEOUT_SECONDS=$(OPENAI_TIMEOUT_SECONDS) \
	uv run python -m scripts.openai_structured_smoke

reset-kz-agents: ## Replace all agents with the canonical Kazakhstan government roster
	cd $(BACKEND_DIR) && uv run python -m scripts.seed_agents --replace-existing

format: ## Run available formatters/linters
	$(MAKE) format-backend
	$(MAKE) format-frontend

format-backend: ## Format backend Python files with Ruff
	cd $(BACKEND_DIR) && uv run ruff format .

format-frontend: ## Format frontend files
	cd $(FRONTEND_DIR) && bun run format
