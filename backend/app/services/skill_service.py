from __future__ import annotations

from pathlib import Path

from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.exceptions import ConflictError, NotFoundError
from app.core.utils import ensure_directory
from app.models.agent import Agent
from app.models.skill import Skill


def _skills_dir() -> Path:
    settings = get_settings()
    return ensure_directory(settings.skills_dir_path)


def _write_skill_file(key: str, content_md: str) -> str:
    skills_dir = _skills_dir()
    file_path = skills_dir / f"{key}.md"
    file_path.write_text(content_md, encoding="utf-8")
    return str(file_path)


def _read_skill_file(file_path: str) -> str:
    p = Path(file_path)
    if p.exists():
        return p.read_text(encoding="utf-8")
    return ""


def create_skill(
    session: Session,
    key: str,
    name: str,
    description: str | None,
    content_md: str,
) -> Skill:
    existing = session.exec(select(Skill).where(Skill.key == key)).first()
    if existing is not None:
        raise ConflictError(f"Skill key '{key}' already exists.")

    file_path = _write_skill_file(key, content_md)

    skill = Skill(
        key=key,
        name=name,
        description=description,
        content_md=content_md,
        file_path=file_path,
    )
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill


def list_skills(session: Session) -> list[Skill]:
    return list(session.exec(select(Skill).order_by(Skill.created_at.desc())))


def get_skill(session: Session, skill_id: str) -> Skill:
    skill = session.get(Skill, skill_id)
    if skill is None:
        raise NotFoundError(f"Skill '{skill_id}' was not found.")
    return skill


def update_skill(
    session: Session,
    skill_id: str,
    name: str | None = None,
    description: str | None = None,
    content_md: str | None = None,
) -> Skill:
    skill = get_skill(session, skill_id)

    if name is not None:
        skill.name = name
    if description is not None:
        skill.description = description
    if content_md is not None:
        skill.content_md = content_md
        skill.file_path = _write_skill_file(skill.key, content_md)

    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill


def delete_skill(session: Session, skill_id: str) -> None:
    skill = get_skill(session, skill_id)
    if skill.file_path:
        p = Path(skill.file_path)
        if p.exists():
            p.unlink()
    session.delete(skill)
    session.commit()


def attach_skills_to_agent(
    session: Session, agent_id: str, skill_ids: list[str]
) -> Agent:
    agent = session.get(Agent, agent_id)
    if agent is None:
        raise NotFoundError(f"Agent '{agent_id}' was not found.")

    existing_skill_ids = {s.id for s in agent.skills}

    for skill_id in skill_ids:
        if skill_id in existing_skill_ids:
            continue
        skill = get_skill(session, skill_id)
        agent.skills.append(skill)

    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent


def detach_skills_from_agent(
    session: Session, agent_id: str, skill_ids: list[str]
) -> Agent:
    agent = session.get(Agent, agent_id)
    if agent is None:
        raise NotFoundError(f"Agent '{agent_id}' was not found.")

    agent.skills = [s for s in agent.skills if s.id not in skill_ids]

    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent


def get_agent_skills_content(session: Session, agent_id: str) -> list[dict[str, str]]:
    agent = session.get(Agent, agent_id)
    if agent is None:
        raise NotFoundError(f"Agent '{agent_id}' was not found.")

    results = []
    for skill in agent.skills:
        content = skill.content_md
        if not content and skill.file_path:
            content = _read_skill_file(skill.file_path)
        results.append({
            "skill_id": skill.id,
            "key": skill.key,
            "name": skill.name,
            "content_md": content or "",
        })
    return results
