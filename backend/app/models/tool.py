from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Column, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.core.utils import utc_now
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class AgentToolLink(SQLModel, table=True):
    __tablename__ = "agent_tools"
    __table_args__ = (UniqueConstraint("agent_id", "tool_id", name="uq_agent_tool_link"),)

    agent_id: str = Field(foreign_key="agents.id", primary_key=True, max_length=36)
    tool_id: str = Field(foreign_key="tools.id", primary_key=True, max_length=36)
    config_override_json: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column("config_override", JSON, nullable=False, server_default="{}"),
    )
    created_at: datetime = Field(default_factory=utc_now, nullable=False)


if TYPE_CHECKING:
    from app.models.agent import Agent


class Tool(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    __tablename__ = "tools"

    name: str = Field(unique=True, index=True, max_length=255)
    description: str | None = Field(default=None)
    tool_type: str = Field(default="custom", max_length=50)
    input_schema_json: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column("schema_json", JSON, nullable=False),
    )
    output_schema_json: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column("output_schema_json", JSON, nullable=False, server_default="{}"),
    )
    configuration_json: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column("configuration_json", JSON, nullable=False, server_default="{}"),
    )
    endpoint_url: str | None = Field(default=None, max_length=1024)

    agents: list["Agent"] = Relationship(back_populates="tools", link_model=AgentToolLink)
