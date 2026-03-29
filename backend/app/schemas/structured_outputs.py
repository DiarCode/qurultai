from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RoutingDecision(BaseModel):
    mode: Literal["direct_answer", "rag_answer", "specialist_assist", "council"]
    complexity_level: Literal["simple", "moderate", "complex", "high_risk"] = "simple"
    rationale: str = Field(min_length=1)
    should_use_retrieval: bool = False
    delegation_reasons: list[str] = Field(default_factory=list)
    selected_agent_keys: list[str] = Field(default_factory=list)


class SpecialistAnalysis(BaseModel):
    summary: str = Field(min_length=1)
    key_findings: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommendation: str = Field(min_length=1)


class FinalAnswerPayload(BaseModel):
    answer_markdown: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    key_points: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    uncertainty: str | None = None
    suggested_next_steps: list[str] = Field(default_factory=list)
    report_title: str = Field(default="Qurultai Report")


class GoalPlan(BaseModel):
    mission_goals: list[str] = Field(default_factory=list, min_length=1)


class LangGraphBidPlan(BaseModel):
    selected_agent_ids: list[str] = Field(default_factory=list)


class CriticDecision(BaseModel):
    has_conflict: bool
    reason: str = Field(min_length=1)


class ConsolidatedReportPayload(BaseModel):
    title: str = Field(default="Final Consolidated Report")
    executive_summary: str = Field(min_length=1)
    mission_goals: list[str] = Field(default_factory=list)
    tradeoffs: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
