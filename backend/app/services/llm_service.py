from __future__ import annotations

from collections.abc import Iterator
from functools import lru_cache
from typing import Any, TypeVar

from pydantic import BaseModel

from app.core.config import get_settings

StructuredResponseT = TypeVar("StructuredResponseT", bound=BaseModel)


class LLMDisabledError(RuntimeError):
    pass


def _ensure_enabled() -> None:
    settings = get_settings()
    if not settings.ENABLE_LLM_CALLS:
        raise LLMDisabledError("LLM calls are disabled in this environment.")


def _provider_label() -> str:
    return get_settings().LLM_PROVIDER.lower().strip()


def _provider_model_name() -> str:
    settings = get_settings()
    provider = _provider_label()
    if provider == "openai":
        return settings.OPENAI_MODEL
    return settings.OLLAMA_MODEL


def _build_system_prompt(
    system_prompt: str | None = None,
    *,
    context: str | None = None,
    skills_content: list[str] | None = None,
) -> str | None:
    blocks: list[str] = []

    if system_prompt and system_prompt.strip():
        blocks.append(system_prompt.strip())

    if skills_content:
        rendered_skills = "\n\n".join(
            skill.strip() for skill in skills_content if skill and skill.strip()
        )
        if rendered_skills:
            blocks.append(f"## Specialist Guidance\n{rendered_skills}")

    if context and context.strip():
        blocks.append(f"## Grounded Context\n{context.strip()}")

    if not blocks:
        return None

    return "\n\n".join(blocks)


def _stringify_content(content: Any, *, preserve_whitespace: bool = False) -> str:
    if isinstance(content, str):
        return content if preserve_whitespace else content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
                continue
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        if preserve_whitespace:
            return "".join(parts)
        return "\n".join(fragment.strip() for fragment in parts if fragment and fragment.strip())
    return str(content) if preserve_whitespace else str(content).strip()


@lru_cache(maxsize=1)
def _get_openai_client():
    settings = get_settings()
    from openai import OpenAI

    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    return OpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
        timeout=settings.OPENAI_TIMEOUT_SECONDS,
    )


@lru_cache(maxsize=16)
def get_langchain_chat_model(
    *,
    max_completion_tokens: int | None = None,
    streaming: bool = False,
):
    settings = get_settings()

    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
        temperature=settings.OPENAI_TEMPERATURE,
        timeout=settings.OPENAI_TIMEOUT_SECONDS,
        streaming=streaming,
        max_completion_tokens=max_completion_tokens,
    )


def _invoke_openai(
    *,
    prompt: str,
    system_prompt: str | None = None,
    context: str | None = None,
    skills_content: list[str] | None = None,
    max_output_tokens: int | None = None,
) -> str:
    from langchain_core.messages import HumanMessage, SystemMessage

    rendered_system = _build_system_prompt(
        system_prompt, context=context, skills_content=skills_content
    )
    messages: list[SystemMessage | HumanMessage] = []
    if rendered_system:
        messages.append(SystemMessage(content=rendered_system))
    messages.append(HumanMessage(content=prompt))
    response = get_langchain_chat_model(max_completion_tokens=max_output_tokens).invoke(messages)
    return _stringify_content(response.content)


def _stream_openai(
    *,
    prompt: str,
    system_prompt: str | None = None,
    context: str | None = None,
    skills_content: list[str] | None = None,
    max_output_tokens: int | None = None,
) -> Iterator[str]:
    from langchain_core.messages import HumanMessage, SystemMessage

    rendered_system = _build_system_prompt(
        system_prompt, context=context, skills_content=skills_content
    )
    messages: list[SystemMessage | HumanMessage] = []
    if rendered_system:
        messages.append(SystemMessage(content=rendered_system))
    messages.append(HumanMessage(content=prompt))

    for chunk in get_langchain_chat_model(
        max_completion_tokens=max_output_tokens,
        streaming=True,
    ).stream(messages):
        text = _stringify_content(getattr(chunk, "content", chunk), preserve_whitespace=True)
        if text:
            yield text


@lru_cache(maxsize=16)
def _get_ollama_client(*, num_predict: int | None = None):
    settings = get_settings()
    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=settings.OPENAI_TEMPERATURE,
        num_predict=num_predict or settings.OLLAMA_NUM_PREDICT,
        validate_model_on_init=False,
        sync_client_kwargs={"timeout": settings.OPENAI_TIMEOUT_SECONDS},
    )


def _invoke_ollama(
    *,
    prompt: str,
    system_prompt: str | None = None,
    context: str | None = None,
    skills_content: list[str] | None = None,
    max_output_tokens: int | None = None,
) -> str:
    from langchain_core.messages import HumanMessage, SystemMessage

    rendered_system = _build_system_prompt(
        system_prompt, context=context, skills_content=skills_content
    )
    messages: list[SystemMessage | HumanMessage] = []
    if rendered_system:
        messages.append(SystemMessage(content=rendered_system))
    messages.append(HumanMessage(content=prompt))
    response = _get_ollama_client(num_predict=max_output_tokens).invoke(messages)
    return _stringify_content(response.content)


def _stream_ollama(
    *,
    prompt: str,
    system_prompt: str | None = None,
    context: str | None = None,
    skills_content: list[str] | None = None,
    max_output_tokens: int | None = None,
) -> Iterator[str]:
    from langchain_core.messages import HumanMessage, SystemMessage

    rendered_system = _build_system_prompt(
        system_prompt, context=context, skills_content=skills_content
    )
    messages: list[SystemMessage | HumanMessage] = []
    if rendered_system:
        messages.append(SystemMessage(content=rendered_system))
    messages.append(HumanMessage(content=prompt))

    for chunk in _get_ollama_client(num_predict=max_output_tokens).stream(messages):
        text = _stringify_content(getattr(chunk, "content", chunk), preserve_whitespace=True)
        if text:
            yield text


def _invoke(
    *,
    prompt: str,
    system_prompt: str | None = None,
    context: str | None = None,
    skills_content: list[str] | None = None,
    max_output_tokens: int | None = None,
) -> str:
    _ensure_enabled()
    provider = _provider_label()

    if provider == "openai":
        return _invoke_openai(
            prompt=prompt,
            system_prompt=system_prompt,
            context=context,
            skills_content=skills_content,
            max_output_tokens=max_output_tokens,
        )
    if provider == "ollama":
        return _invoke_ollama(
            prompt=prompt,
            system_prompt=system_prompt,
            context=context,
            skills_content=skills_content,
            max_output_tokens=max_output_tokens,
        )
    raise RuntimeError(f"Unsupported LLM provider '{get_settings().LLM_PROVIDER}'.")


def invoke_llm(
    prompt: str,
    system_prompt: str | None = None,
    *,
    max_output_tokens: int | None = None,
) -> str:
    return _invoke(
        prompt=prompt,
        system_prompt=system_prompt,
        max_output_tokens=max_output_tokens,
    )


def invoke_llm_with_context(
    prompt: str,
    system_prompt: str | None = None,
    context: str | None = None,
    skills_content: list[str] | None = None,
    max_output_tokens: int | None = None,
) -> str:
    return _invoke(
        prompt=prompt,
        system_prompt=system_prompt,
        context=context,
        skills_content=skills_content,
        max_output_tokens=max_output_tokens,
    )


def stream_llm_with_context(
    prompt: str,
    system_prompt: str | None = None,
    context: str | None = None,
    skills_content: list[str] | None = None,
    max_output_tokens: int | None = None,
) -> Iterator[str]:
    _ensure_enabled()
    provider = _provider_label()

    if provider == "openai":
        yield from _stream_openai(
            prompt=prompt,
            system_prompt=system_prompt,
            context=context,
            skills_content=skills_content,
            max_output_tokens=max_output_tokens,
        )
        return
    if provider == "ollama":
        yield from _stream_ollama(
            prompt=prompt,
            system_prompt=system_prompt,
            context=context,
            skills_content=skills_content,
            max_output_tokens=max_output_tokens,
        )
        return
    raise RuntimeError(f"Unsupported LLM provider '{get_settings().LLM_PROVIDER}'.")


def invoke_structured(
    *,
    prompt: str,
    response_model: type[StructuredResponseT],
    system_prompt: str | None = None,
    context: str | None = None,
    skills_content: list[str] | None = None,
    max_output_tokens: int | None = None,
) -> StructuredResponseT:
    _ensure_enabled()

    if _provider_label() != "openai":
        raise RuntimeError("Structured outputs are only configured for the OpenAI provider.")

    settings = get_settings()
    rendered_system = _build_system_prompt(
        system_prompt, context=context, skills_content=skills_content
    )
    parsed = _get_openai_client().responses.parse(
        model=settings.OPENAI_MODEL,
        instructions=rendered_system,
        input=prompt,
        text_format=response_model,
        temperature=settings.OPENAI_TEMPERATURE,
        max_output_tokens=max_output_tokens,
    )
    output_parsed = getattr(parsed, "output_parsed", None)
    if output_parsed is None:
        raise RuntimeError("Structured response parsing returned no output.")
    return output_parsed


def check_llm_health() -> dict[str, str | None]:
    settings = get_settings()
    provider = _provider_label()
    model = _provider_model_name()

    if not settings.ENABLE_LLM_CALLS:
        return {
            "status": "disabled",
            "provider": provider,
            "model": model,
            "response": None,
            "error": None,
        }

    try:
        response = _invoke(prompt="Reply with the single word pong.")
        return {
            "status": "ok",
            "provider": provider,
            "model": model,
            "response": response[:80],
            "error": None,
        }
    except Exception as exc:
        return {
            "status": "error",
            "provider": provider,
            "model": model,
            "response": None,
            "error": str(exc),
        }
