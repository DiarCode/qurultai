from __future__ import annotations

from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.services import llm_service


class SmokePayload(BaseModel):
    answer: str = Field(min_length=1)
    bullets: list[str] = Field(default_factory=list)


def main() -> None:
    settings = get_settings()
    print("provider", settings.LLM_PROVIDER)
    print("model", settings.OPENAI_MODEL)
    print("enabled", settings.ENABLE_LLM_CALLS)
    print("has_key", bool(settings.OPENAI_API_KEY))

    text = llm_service.invoke_llm(
        "In one sentence, say that the OpenAI smoke test is working.",
        system_prompt="Respond in plain English.",
    )
    print("text_response", text)

    streamed_chunks = list(
        llm_service.stream_llm_with_context(
            "Write two short markdown bullets proving live streaming is working.",
            system_prompt="Return only markdown bullets.",
        )
    )
    print("stream_chunk_count", len(streamed_chunks))
    print("stream_preview", "".join(streamed_chunks)[:160])

    structured = llm_service.invoke_structured(
        prompt="Return a short success message and exactly two bullets that prove structured output works.",
        response_model=SmokePayload,
        system_prompt="You are a smoke test assistant. Return structured output only.",
    )
    print("structured_answer", structured.answer)
    print("structured_bullets", structured.bullets)


if __name__ == "__main__":
    main()
