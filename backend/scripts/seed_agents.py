"""Seed the database with predefined agents, skills, and tools.

Usage:
    python -m scripts.seed_agents          # from backend/
    uv run python -m scripts.seed_agents   # with uv
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from sqlmodel import Session, select

from app.db.engine import engine
from app.models.agent import Agent
from app.models.tool import Tool
from app.services.database_service import initialize_database

try:
    from app.models.skill import Skill  # type: ignore
except Exception:
    Skill = None  # type: ignore[assignment]

SKILLS_DIR = Path(__file__).resolve().parent.parent / "data" / "skills"
PROMPTS_DIR = Path(__file__).resolve().parent.parent / "data" / "prompts"


# ---------------------------------------------------------------------------
# Skill definitions
# ---------------------------------------------------------------------------
SKILLS = [
    {
        "key": "economy_analysis",
        "name": "Экономический анализ",
        "description": "Анализ экономических аспектов решений: макроэкономика, инвестиции, предпринимательство, ГЧП",
        "file_path": "data/skills/economy_analysis.md",
    },
    {
        "key": "legal_analysis",
        "name": "Правовой анализ",
        "description": "Анализ правовых аспектов: НПА, разрешения, соответствие законодательству, судебная практика",
        "file_path": "data/skills/legal_analysis.md",
    },
    {
        "key": "environmental_analysis",
        "name": "Экологический анализ",
        "description": "Экологическая экспертиза: ОВОС, выбросы, отходы, водные ресурсы, земельные ресурсы",
        "file_path": "data/skills/environmental_analysis.md",
    },
    {
        "key": "finance_budget_analysis",
        "name": "Финансово-бюджетный анализ",
        "description": "Анализ бюджетных последствий, налоговый эффект, государственный долг, Национальный фонд",
        "file_path": "data/skills/finance_budget_analysis.md",
    },
    {
        "key": "labor_social_analysis",
        "name": "Анализ труда и социальной политики",
        "description": "Трудовое право, занятость, социальное страхование, демография, социальная защита",
        "file_path": "data/skills/labor_social_analysis.md",
    },
]


# ---------------------------------------------------------------------------
# Tool definitions (built-in)
# ---------------------------------------------------------------------------
TOOLS = [
    {
        "name": "pdf_reader",
        "description": "Извлечение текста из PDF-документов",
        "tool_type": "builtin",
        "input_schema_json": {"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]},
    },
    {
        "name": "html_reader",
        "description": "Извлечение текста из HTML-страниц",
        "tool_type": "builtin",
        "input_schema_json": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]},
    },
    {
        "name": "ocr_reader",
        "description": "Распознавание текста на изображениях (OCR)",
        "tool_type": "builtin",
        "input_schema_json": {"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]},
    },
]


# ---------------------------------------------------------------------------
# Agent definitions
# ---------------------------------------------------------------------------

def _load_prompt(filename: str) -> str:
    path = PROMPTS_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return f"System prompt file not found: {filename}"


AGENTS = [
    {
        "key": "orchestrator",
        "name": "Оркестратор",
        "role_description": "Координатор сессии — декомпозиция запросов, распределение задач, контроль качества",
        "prompt_file": "orchestrator.md",
        "goals": [
            "Декомпозировать запрос пользователя на 3-5 измеримых целей (mission_goals)",
            "Определить необходимых специалистов для каждой цели",
            "Обеспечить полноту и согласованность анализа",
            "Контролировать качество заключений специалистов",
        ],
        "constraints": [
            "Не подменять экспертное мнение специалистов",
            "Не принимать решений за пользователя",
            "Всегда отвечать на русском языке",
            "Учитывать только законодательство Республики Казахстан",
        ],
        "skills": [],
        "tools": [],
    },
    {
        "key": "economy_analyst",
        "name": "Аналитик-экономист",
        "role_description": "Эксперт по экономическому анализу — макроэкономика, инвестиции, предпринимательство, ГЧП",
        "prompt_file": "economy_analyst.md",
        "goals": [
            "Провести макроэкономический анализ с учётом структуры экономики РК",
            "Оценить инвестиционную привлекательность и применимые преференции",
            "Рассчитать экономический эффект (вклад в ВВП, занятость, экспорт)",
            "Определить экономические риски и предложить меры их минимизации",
        ],
        "constraints": [
            "Подкреплять выводы конкретными данными и ссылками на НПА",
            "Использовать сценарный подход (минимум 2 сценария)",
            "Учитывать сырьевую зависимость экономики РК",
            "Всегда отвечать на русском языке",
        ],
        "skills": ["economy_analysis"],
        "tools": ["pdf_reader", "html_reader"],
    },
    {
        "key": "legal_analyst",
        "name": "Аналитик-юрист",
        "role_description": "Эксперт по правовому анализу — НПА, разрешения, регуляторное соответствие, судебные перспективы",
        "prompt_file": "legal_analyst.md",
        "goals": [
            "Определить применимое законодательство с указанием конкретных статей",
            "Оценить соответствие действующим НПА и выявить правовые коллизии",
            "Определить необходимые разрешения, лицензии и процедуры",
            "Оценить правовые риски и ответственность",
        ],
        "constraints": [
            "Указывать конкретные статьи, пункты и подпункты НПА",
            "Учитывать иерархию НПА (Конституция → кодексы → законы → подзаконные акты)",
            "Толковать неопределённости в пользу субъекта предпринимательства",
            "Всегда отвечать на русском языке",
        ],
        "skills": ["legal_analysis"],
        "tools": ["pdf_reader", "html_reader"],
    },
    {
        "key": "environmental_analyst",
        "name": "Аналитик-эколог",
        "role_description": "Эксперт по экологическому анализу — ОВОС, экологические разрешения, НДТ, охрана природы",
        "prompt_file": "environmental_analyst.md",
        "goals": [
            "Определить категорию объекта (I-IV) по Экологическому кодексу",
            "Оценить воздействие на все компоненты окружающей среды",
            "Определить необходимые экологические процедуры и разрешения",
            "Предложить меры по минимизации экологического воздействия (НДТ)",
        ],
        "constraints": [
            "Применять Экологический кодекс РК (К2021000400)",
            "Учитывать кумулятивное воздействие с существующими объектами",
            "Приоритет предупреждения загрязнения перед ликвидацией",
            "Всегда отвечать на русском языке",
        ],
        "skills": ["environmental_analysis"],
        "tools": ["pdf_reader", "html_reader", "ocr_reader"],
    },
    {
        "key": "finance_analyst",
        "name": "Аналитик по финансам и бюджету",
        "role_description": "Эксперт по государственным финансам — бюджет, налоги, Нацфонд, денежно-кредитная политика",
        "prompt_file": "finance_analyst.md",
        "goals": [
            "Оценить бюджетные последствия (доходы/расходы/баланс)",
            "Рассчитать налоговый эффект с учётом льгот и преференций",
            "Определить источники финансирования и их доступность",
            "Оценить фискальную устойчивость (ненефтяной дефицит, гос. долг)",
        ],
        "constraints": [
            "Все расчёты в тенге и % ВВП",
            "Минимум 3 сценария (базовый, оптимистичный, пессимистичный)",
            "Учитывать зависимость бюджета от нефтяных доходов",
            "Всегда отвечать на русском языке",
        ],
        "skills": ["finance_budget_analysis"],
        "tools": ["pdf_reader", "html_reader"],
    },
    {
        "key": "labor_analyst",
        "name": "Аналитик по труду и социальной политике",
        "role_description": "Эксперт по трудовому праву и социальной политике — занятость, охрана труда, социальная защита",
        "prompt_file": "labor_analyst.md",
        "goals": [
            "Оценить влияние на занятость (создание/сокращение рабочих мест)",
            "Проанализировать соответствие Трудовому кодексу РК",
            "Оценить социальные последствия для уязвимых групп населения",
            "Рассчитать социальные обязательства (ОПВ, ОСМС, СО)",
        ],
        "constraints": [
            "Дифференцировать анализ по социальным группам",
            "Учитывать региональные различия",
            "Приводить количественные показатели (население, зарплаты, пособия)",
            "Всегда отвечать на русском языке",
        ],
        "skills": ["labor_social_analysis"],
        "tools": ["pdf_reader", "html_reader"],
    },
    {
        "key": "consolidator",
        "name": "Консолидатор",
        "role_description": "Составитель итогового отчёта — синтез заключений специалистов, выявление противоречий",
        "prompt_file": "consolidator.md",
        "goals": [
            "Собрать и синтезировать заключения всех специалистов",
            "Выявить противоречия и расхождения между экспертами",
            "Сформировать структурированный итоговый отчёт",
            "Приоритизировать рекомендации по срочности и важности",
        ],
        "constraints": [
            "Не подменять выводы специалистов собственным мнением",
            "Показывать обе стороны при наличии противоречий",
            "Следовать установленному формату отчёта",
            "Всегда отвечать на русском языке",
        ],
        "skills": [],
        "tools": [],
    },
]


# ---------------------------------------------------------------------------
# Seed logic
# ---------------------------------------------------------------------------

def seed() -> None:
    initialize_database()

    with Session(engine) as session:
        # -- Skills --
        skill_map: dict[str, Any] = {}
        if Skill is None:
            print("  Skill model is not available in current branch, skipping skills seeding.")
        else:
            for skill_def in SKILLS:
                existing = session.exec(
                    select(Skill).where(Skill.key == skill_def["key"])
                ).first()
                if existing:
                    print(f"  Skill '{skill_def['key']}' already exists, skipping.")
                    skill_map[skill_def["key"]] = existing
                    continue

                md_path = SKILLS_DIR / f"{skill_def['key']}.md"
                content_md = md_path.read_text(encoding="utf-8") if md_path.exists() else ""

                skill = Skill(
                    key=skill_def["key"],
                    name=skill_def["name"],
                    description=skill_def["description"],
                    content_md=content_md,
                    file_path=skill_def["file_path"],
                )
                session.add(skill)
                session.flush()
                skill_map[skill_def["key"]] = skill
                print(f"  + Skill '{skill_def['key']}' created.")

        # -- Tools --
        tool_map: dict[str, Tool] = {}
        for tool_def in TOOLS:
            existing = session.exec(
                select(Tool).where(Tool.name == tool_def["name"])
            ).first()
            if existing:
                print(f"  Tool '{tool_def['name']}' already exists, skipping.")
                tool_map[tool_def["name"]] = existing
                continue

            tool = Tool(
                name=tool_def["name"],
                description=tool_def["description"],
                input_schema_json=tool_def["input_schema_json"],
                endpoint_url=None,
            )
            session.add(tool)
            session.flush()
            tool_map[tool_def["name"]] = tool
            print(f"  + Tool '{tool_def['name']}' created.")

        # -- Agents --
        for agent_def in AGENTS:
            existing = session.exec(
                select(Agent).where(Agent.key == agent_def["key"])
            ).first()
            if existing:
                print(f"  Agent '{agent_def['key']}' already exists, skipping.")
                continue

            system_prompt = _load_prompt(agent_def["prompt_file"])

            agent = Agent(
                key=agent_def["key"],
                name=agent_def["name"],
                role_description=agent_def["role_description"],
                system_prompt=system_prompt,
                goals_json=agent_def["goals"],
                constraints_json=agent_def["constraints"],
                status="active",
            )
            if hasattr(agent, "skills"):
                agent.skills = [
                    skill_map[sk] for sk in agent_def["skills"] if sk in skill_map
                ]
            agent.tools = [
                tool_map[tl] for tl in agent_def["tools"] if tl in tool_map
            ]
            session.add(agent)
            print(f"  + Agent '{agent_def['key']}' created "
                  f"(skills={len(getattr(agent, 'skills', []))}, tools={len(agent.tools)}).")

        session.commit()
        print("\nSeed completed successfully.")


if __name__ == "__main__":
    seed()
