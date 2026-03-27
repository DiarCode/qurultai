from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    ANALYST = "analyst"
    OPERATOR = "operator"


class AgentStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"


class KnowledgeSourceType(StrEnum):
    DOCUMENT_LIBRARY = "document_library"
    EXTERNAL_API = "external_api"
    URL = "url"
    MANUAL = "manual"


class KnowledgeSourceStatus(StrEnum):
    DRAFT = "draft"
    READY = "ready"
    ARCHIVED = "archived"


class DocumentIndexingStatus(StrEnum):
    PENDING = "pending"
    INDEXED = "indexed"
    FAILED = "failed"


class CaseRequestType(StrEnum):
    POLICY = "policy"
    REGULATORY = "regulatory"
    BRIEFING = "briefing"
    INCIDENT = "incident"
    ADVISORY = "advisory"


class AudienceMode(StrEnum):
    EXECUTIVE = "executive"
    ANALYST = "analyst"
    PUBLIC = "public"


class InputMode(StrEnum):
    MANUAL = "manual"
    DOCUMENT = "document"
    HYBRID = "hybrid"


class CaseStatus(StrEnum):
    SUBMITTED = "submitted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class AuthorType(StrEnum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class MessageType(StrEnum):
    SUBMISSION = "submission"
    DELIBERATION = "deliberation"
    NOTE = "note"
    TOOL = "tool"
    FINAL = "final"


class RunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ReportStatus(StrEnum):
    DRAFT = "draft"
    GENERATED = "generated"
    PUBLISHED = "published"
