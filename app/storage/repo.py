from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime

from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.engine.url import make_url

from app.config import settings
from app.storage.models import Base, User, Event, PremiumRequest


# 👇 гарантируем, что папка для SQLite существует
def _ensure_sqlite_dir(db_url: str):
    try:
        u = make_url(db_url)
        if u.drivername == "sqlite" and u.database:
            os.makedirs(os.path.dirname(u.database), exist_ok=True)
    except Exception:
        # не мешаем запуску, даже если проверка упала
        pass


# вызвать до инициализации движка
_ensure_sqlite_dir(settings.db_url)

engine = create_engine(settings.db_url, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False, autocommit=False)


def init_db() -> None:
    """
    Создаёт недостающие таблицы и «мягко» добавляет недостающие колонки
    для users.source / leads.track (SQLite и Postgres).
    """
    Base.metadata.create_all(engine)

    with Session(engine) as s:
        url = settings.db_url.lower()

        if url.startswith("sqlite"):
            cols = s.execute(text("PRAGMA table_info(users)")).fetchall()
            names = {c[1] for c in cols}
            if "source" not in names:
                s.execute(text("ALTER TABLE users ADD COLUMN source TEXT"))
                s.commit()

            cols = s.execute(text("PRAGMA table_info(leads)")).fetchall()
            names = {c[1] for c in cols}
            if "track" not in names:
                s.execute(text("ALTER TABLE leads ADD COLUMN track TEXT"))
                s.commit()
        else:
            # Postgres / другие диалекты
            s.execute(text("ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS source varchar(64)"))
            s.execute(text("ALTER TABLE IF EXISTS leads ADD COLUMN IF NOT EXISTS track varchar(32)"))
            s.commit()


@contextmanager
def session_scope() -> Session:
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def delete_user_cascade(s: Session, user_id: int | None = None, tg_id: int | None = None) -> bool:
    if user_id is None and tg_id is None:
        return False

    q = s.query(User)
    u = q.filter_by(id=user_id).first() if user_id is not None else q.filter_by(tg_id=tg_id).first()
    if not u:
        return False

    s.delete(u)
    s.commit()
    return True


def log_event(s: Session, user_id: int | None, name: str, payload: dict | None = None) -> None:
    """Лог с защитой от сбоев: проблемы логов не ломают основной поток."""
    try:
        s.add(Event(
            user_id=user_id,
            kind=name,
            payload_json=(payload or {}),
            ts=datetime.utcnow(),
        ))
        s.commit()
    except Exception:
        s.rollback()
        # намеренно молчим — лог вспомогательный


# ---------- Премиум: CRUD (вариант 2 «как надо») ----------

def add_premium_request(user_id: int, tg_username: str | None) -> PremiumRequest:
    """
    Создаёт новую заявку, но если у пользователя уже есть 'new' или 'in_review',
    возвращаем её (без дубликатов).
    """
    with SessionLocal() as s:
        existing = s.execute(
            select(PremiumRequest)
            .where(
                PremiumRequest.user_id == user_id,
                PremiumRequest.status.in_(("new", "in_review")),
            )
            .order_by(PremiumRequest.id.desc())
        ).scalar_one_or_none()

        if existing:
            return existing

        pr = PremiumRequest(user_id=user_id, tg_username=tg_username or None, status="new")
        s.add(pr)
        s.commit()
        s.refresh(pr)
        return pr


def list_user_premium_requests(user_id: int, limit: int = 10) -> list[PremiumRequest]:
    with SessionLocal() as s:
        rows = s.execute(
            select(PremiumRequest)
            .where(PremiumRequest.user_id == user_id)
            .order_by(PremiumRequest.id.desc())
            .limit(limit)
        ).scalars().all()
        return list(rows)
