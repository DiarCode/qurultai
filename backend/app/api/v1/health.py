from fastapi import APIRouter

from app.api.deps import SessionDep
from app.controllers.health_controller import get_health
from app.schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
def health_check(session: SessionDep) -> HealthResponse:
    return get_health(session)
