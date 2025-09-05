from __future__ import annotations

from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.storage.models import Base

# Engine / Session
engine = create_engine(settings.db_url, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False, autocommit=False)


def init_db() -> None:
    """
    Создаёт таблицы и, при необходимости, добавляет отсутствующую колонку users.source.
    Безопасно как для SQLite, так и для Postgres.
    """
    # базовые таблицы
    Base.metadata.create_all(engine)

    with Session(engine) as s:
        url = settings.db_url.lower()

        if url.startswith("sqlite"):
            # Проверяем, есть ли колонка 'source' в таблице users
            cols = s.execute(text("PRAGMA table_info(users)")).fetchall()
            names = {c[1] for c in cols}  # второй столбец = name
            if "source" not in names:
                s.execute(text("ALTER TABLE users ADD COLUMN source TEXT"))
                s.commit()
        else:
            # Postgres и пр.: IF NOT EXISTS
            s.execute(text("ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS source varchar(64)"))
            s.commit()


@contextmanager
def session_scope() -> Session:
    """Контекстный менеджер для сессии БД."""
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
