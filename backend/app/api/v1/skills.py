from fastapi import APIRouter

from app.api.deps import SessionDep
from app.schemas.skills import (
    SkillCreate,
    SkillRead,
    SkillUpdate,
)
from app.services import skill_service

router = APIRouter(prefix="/skills", tags=["skills"])


@router.post("", response_model=SkillRead, status_code=201)
def create_skill(payload: SkillCreate, session: SessionDep) -> SkillRead:
    skill = skill_service.create_skill(
        session,
        key=payload.key,
        name=payload.name,
        description=payload.description,
        content_md=payload.content_md,
    )
    return SkillRead.model_validate(skill)


@router.get("", response_model=list[SkillRead])
def list_skills(session: SessionDep) -> list[SkillRead]:
    return [SkillRead.model_validate(s) for s in skill_service.list_skills(session)]


@router.get("/{skill_id}", response_model=SkillRead)
def get_skill(skill_id: str, session: SessionDep) -> SkillRead:
    return SkillRead.model_validate(skill_service.get_skill(session, skill_id))


@router.patch("/{skill_id}", response_model=SkillRead)
def update_skill(skill_id: str, payload: SkillUpdate, session: SessionDep) -> SkillRead:
    skill = skill_service.update_skill(
        session,
        skill_id,
        name=payload.name,
        description=payload.description,
        content_md=payload.content_md,
    )
    return SkillRead.model_validate(skill)


@router.delete("/{skill_id}", status_code=204)
def delete_skill(skill_id: str, session: SessionDep) -> None:
    skill_service.delete_skill(session, skill_id)
