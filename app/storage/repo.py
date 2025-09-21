from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.storage.models import Base  # должен экспортировать Base и модели

# Engine + Session
engine = create_engine(settings.db_url, future=True)
SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True
)

@contextmanager
def session_scope() -> Iterator:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def ensure_schema():
    """
    Простой dev-bootstrap:
    - если таблиц нет — создаём по ORM (Base.metadata.create_all).
    - Если используете Alembic — этот шаг не мешает (создаст только отсутствующее).
    """
    insp = inspect(engine)
    if not insp.has_table("users"):
        Base.metadata.create_all(bind=engine)
