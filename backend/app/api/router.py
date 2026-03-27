from fastapi import APIRouter

from app.api.v1.agents import router as agents_router
from app.api.v1.health import router as health_router
from app.api.v1.rooms import router as rooms_router
from app.core.constants import API_V1_PREFIX

api_router = APIRouter()
v1_router = APIRouter(prefix=API_V1_PREFIX)
v1_router.include_router(health_router)
v1_router.include_router(agents_router)
v1_router.include_router(rooms_router)
api_router.include_router(v1_router)
