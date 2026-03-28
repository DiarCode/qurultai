from __future__ import annotations

from app.db.base import SQLModel
from app.db.engine import engine


def _ensure_knowledge_tables_schema() -> None:
    required_columns = {
        "id",
        "title",
        "source_filename",
        "mime_type",
        "size_bytes",
        "s3_bucket",
        "s3_key",
        "text_preview",
        "metadata_json",
        "created_at",
        "updated_at",
    }

    with engine.begin() as connection:
        rows = connection.exec_driver_sql("PRAGMA table_info('knowledge_documents')").fetchall()
        if not rows:
            return

        existing_columns = {row[1] for row in rows}
        if required_columns.issubset(existing_columns):
            return

        # Local dev compatibility: recreate only the mismatched knowledge tables.
        connection.exec_driver_sql("DROP TABLE IF EXISTS agent_knowledge_documents")
        connection.exec_driver_sql("DROP TABLE IF EXISTS knowledge_documents")


def init_db() -> None:
    _ensure_knowledge_tables_schema()
    SQLModel.metadata.create_all(engine)
