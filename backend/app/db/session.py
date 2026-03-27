from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

from app.db.engine import engine

SessionLocal = sessionmaker(bind=engine, class_=Session, autoflush=False, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
