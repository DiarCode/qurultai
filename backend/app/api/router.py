from fastapi import APIRouter

from app.api.v1.agents import router as agents_router
from app.api.v1.audit import router as audit_router
from app.api.v1.cases import router as cases_router
from app.api.v1.health import router as health_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.reports import router as reports_router
from app.core.constants import API_V1_PREFIX

api_router = APIRouter()
v1_router = APIRouter(prefix=API_V1_PREFIX)
v1_router.include_router(health_router)
v1_router.include_router(agents_router)
v1_router.include_router(knowledge_router)
v1_router.include_router(cases_router)
v1_router.include_router(reports_router)
v1_router.include_router(audit_router)
api_router.include_router(v1_router)
