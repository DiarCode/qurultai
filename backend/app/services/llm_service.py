from __future__ import annotations

import logging
from functools import lru_cache

from langchain_ollama import ChatOllama

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_llm() -> ChatOllama:
    settings = get_settings()
    return ChatOllama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        temperature=settings.OLLAMA_TEMPERATURE,
    )


def invoke_llm(prompt: str, system_prompt: str | None = None) -> str:
    llm = get_llm()
    messages = []
    if system_prompt:
        messages.append(("system", system_prompt))
    messages.append(("human", prompt))
    response = llm.invoke(messages)
    return str(response.content)


def invoke_llm_with_context(
    prompt: str,
    system_prompt: str | None = None,
    context: str | None = None,
    skills_content: list[str] | None = None,
) -> str:
    llm = get_llm()
    messages = []

    full_system = system_prompt or ""
    if skills_content:
        full_system += "\n\n## Agent Skills\n"
        for skill in skills_content:
            full_system += f"\n{skill}\n"
    if context:
        full_system += f"\n\n## Context\n{context}"

    if full_system.strip():
        messages.append(("system", full_system))
    messages.append(("human", prompt))

    response = llm.invoke(messages)
    return str(response.content)


def check_ollama_health() -> dict:
    try:
        llm = get_llm()
        response = llm.invoke([("human", "ping")])
        return {"status": "ok", "model": get_settings().OLLAMA_MODEL, "response": str(response.content)[:50]}
    except Exception as e:
        return {"status": "error", "model": get_settings().OLLAMA_MODEL, "error": str(e)}
