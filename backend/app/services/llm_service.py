from __future__ import annotations

import logging
from functools import lru_cache

from openai import OpenAI

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_llm() -> OpenAI:
    settings = get_settings()
    return OpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
        timeout=settings.OPENAI_TIMEOUT_SECONDS,
    )


def invoke_llm(prompt: str, system_prompt: str | None = None) -> str:
    client = get_llm()
    settings = get_settings()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        temperature=settings.OPENAI_TEMPERATURE,
        messages=messages,
    )
    return str((response.choices[0].message.content or "").strip())


def invoke_llm_with_context(
    prompt: str,
    system_prompt: str | None = None,
    context: str | None = None,
    skills_content: list[str] | None = None,
) -> str:
    client = get_llm()
    settings = get_settings()
    messages = []

    full_system = system_prompt or ""
    if skills_content:
        full_system += "\n\n## Agent Skills\n"
        for skill in skills_content:
            full_system += f"\n{skill}\n"
    if context:
        full_system += f"\n\n## Context\n{context}"

    if full_system.strip():
        messages.append({"role": "system", "content": full_system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        temperature=settings.OPENAI_TEMPERATURE,
        messages=messages,
    )
    return str((response.choices[0].message.content or "").strip())


def check_openai_health() -> dict:
    try:
        client = get_llm()
        settings = get_settings()
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=8,
            temperature=0,
        )
        text = str((response.choices[0].message.content or "").strip())
        return {"status": "ok", "model": settings.OPENAI_MODEL, "response": text[:50]}
    except Exception as e:
        return {"status": "error", "model": get_settings().OPENAI_MODEL, "error": str(e)}
