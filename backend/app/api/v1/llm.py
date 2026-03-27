from fastapi import APIRouter

from app.schemas.common import ORMModel
from app.services.llm_service import check_ollama_health


class LLMHealthResponse(ORMModel):
    status: str
    model: str
    response: str | None = None
    error: str | None = None


router = APIRouter(prefix="/llm", tags=["llm"])


@router.get("/health", response_model=LLMHealthResponse)
def llm_health() -> LLMHealthResponse:
    result = check_ollama_health()
    return LLMHealthResponse(**result)
