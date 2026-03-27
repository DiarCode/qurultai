from typing import TYPE_CHECKING

from sqlalchemy import JSON, Column, String
from sqlmodel import Field, Relationship

from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.knowledge_document import AgentKnowledgeLink
from app.models.tool import AgentToolLink

if TYPE_CHECKING:
    from app.models.knowledge_document import KnowledgeDocument
    from app.models.tool import Tool


class Agent(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    __tablename__ = "agents"

    key: str = Field(index=True, unique=True, max_length=100)
    name: str = Field(max_length=255)
    role_description: str = Field(sa_column=Column("role", String, nullable=False))
    system_prompt: str = Field()
    goals_json: list[str] = Field(default_factory=list, sa_type=JSON)
    constraints_json: list[str] = Field(default_factory=list, sa_type=JSON)
    status: str = Field(default="active", max_length=50)

    tools: list["Tool"] = Relationship(back_populates="agents", link_model=AgentToolLink)
    knowledge_documents: list["KnowledgeDocument"] = Relationship(link_model=AgentKnowledgeLink)
