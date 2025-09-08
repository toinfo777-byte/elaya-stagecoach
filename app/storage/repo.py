# app/storage/repo.py
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime  # <-- NEW
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.storage.models import Base, User, Event  # <-- Event для логирования

# Engine / Session
engine = create_engine(settings.db_url, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False, autocommit=False)


def init_db() -> None:
    """
    Создаёт все таблицы моделей (в т.ч. feedbacks) и, при необходимости, добавляет
    отсутствующие колонки:
      - users.source
      - leads.track
    Безопасно как для SQLite, так и для Postgres.
    """
    # создаст недостающие таблицы, включая feedbacks
    Base.metadata.create_all(engine)

    with Session(engine) as s:
        url = settings.db_url.lower()

        if url.startswith("sqlite"):
            # --- users.source ---
            cols = s.execute(text("PRAGMA table_info(users)")).fetchall()
            names = {c[1] for c in cols}
            if "source" not in names:
                s.execute(text("ALTER TABLE users ADD COLUMN source TEXT"))
                s.commit()

            # --- leads.track ---
            cols = s.execute(text("PRAGMA table_info(leads)")).fetchall()
            names = {c[1] for c in cols}
            if "track" not in names:
                s.execute(text("ALTER TABLE leads ADD COLUMN track TEXT"))
                s.commit()

        else:
            # Postgres и др. — с IF NOT EXISTS
            s.execute(text("ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS source varchar(64)"))
            s.execute(text("ALTER TABLE IF EXISTS leads ADD COLUMN IF NOT EXISTS track varchar(32)"))
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


# --- логирование событий (в таблицу events) ---
def log_event(s: Session, user_id: int | None, name: str, payload: dict | None = None) -> None:
    """
    Добавляет запись в events:
      - user_id: необязателен (для системных событий можно None)
      - name: короткое имя/тип события
      - payload: произвольный JSON с деталями
    """
    e = Event(
        user_id=user_id,
        kind=name,
        payload_json=(payload or {}),
        ts=datetime.utcnow(),
    )
    s.add(e)
    s.commit()


# --- каскадное удаление пользователя и всех связанных записей ---
def delete_user_cascade(s: Session, user_id: int | None = None, tg_id: int | None = None) -> bool:
    """
    Удаляет пользователя и всё связанное (drill_runs, leads, events, test_results, feedbacks)
    благодаря cascade='all, delete-orphan' в моделях.
    Можно передать либо user_id (PK), либо tg_id. Возвращает True, если найден и удалён.
    """
    if user_id is None and tg_id is None:
        return False

    q = s.query(User)
    u = q.filter_by(id=user_id).first() if user_id is not None else q.filter_by(tg_id=tg_id).first()
    if not u:
        return False

    s.delete(u)
    s.commit()
    return True
