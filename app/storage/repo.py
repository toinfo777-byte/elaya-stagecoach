from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime
from typing import Iterable

from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.engine.url import make_url

from app.config import settings
from app.storage.models import Base, User, Event, PremiumRequest


# ── ensure sqlite dir ──────────────────────────────────────────────────────────
def _ensure_sqlite_dir(db_url: str):
    try:
        u = make_url(db_url)
        if u.drivername == "sqlite" and u.database:
            os.makedirs(os.path.dirname(u.database), exist_ok=True)
    except Exception:
        pass


_ensure_sqlite_dir(settings.db_url)

engine = create_engine(settings.db_url, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False, autocommit=False)


def init_db() -> None:
    Base.metadata.create_all(engine)

    with Session(engine) as s:
        url = settings.db_url.lower()

        if url.startswith("sqlite"):
            # users.source
            cols = s.execute(text("PRAGMA table_info(users)")).fetchall()
            names = {c[1] for c in cols}
            if "source" not in names:
                s.execute(text("ALTER TABLE users ADD COLUMN source TEXT"))
                s.commit()

            # leads.track
            cols = s.execute(text("PRAGMA table_info(leads)")).fetchall()
            names = {c[1] for c in cols}
            if "track" not in names:
                s.execute(text("ALTER TABLE leads ADD COLUMN track TEXT"))
                s.commit()
        else:
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


# ── helpers ────────────────────────────────────────────────────────────────────
def get_or_create_user_by_tg(s: Session, tg_id: int, username: str | None) -> User:
    u = s.scalar(select(User).where(User.tg_id == tg_id))
    if not u:
        u = User(tg_id=tg_id, username=username)
        s.add(u)
        s.flush()
    else:
        # немного поддерживаем актуальный username
        if username and u.username != username:
            u.username = username
            s.flush()
    return u


def delete_user_cascade(s: Session, user_id: int | None = None, tg_id: int | None = None) -> bool:
    if user_id is None and tg_id is None:
        return False

    if user_id is not None:
        u = s.get(User, user_id)
    else:
        u = s.scalar(select(User).where(User.tg_id == tg_id))

    if not u:
        return False

    s.delete(u)
    s.commit()
    return True


def log_event(s: Session, user_id: int | None, name: str, payload: dict | None = None) -> None:
    try:
        s.add(Event(user_id=user_id, kind=name, payload_json=(payload or {}), ts=datetime.utcnow()))
        s.commit()
    except Exception:
        s.rollback()


# ── Premium requests ───────────────────────────────────────────────────────────
def add_premium_request_for_tg(
    s: Session,
    tg_id: int,
    username: str | None,
    text_note: str | None,
    source: str = "premium",
) -> PremiumRequest:
    """Создаёт заявку для пользователя по tg_id (создаст юзера, если его ещё нет)."""
    user = get_or_create_user_by_tg(s, tg_id, username)
    pr = PremiumRequest(
        user_id=user.id,
        tg_username=username,
        status="new",
        meta={"note": text_note or "", "source": source},
        created_at=datetime.utcnow(),
    )
    s.add(pr)
    s.flush()
    log_event(s, user.id, "premium_request_created", {"request_id": pr.id})
    return pr


def list_premium_requests_for_tg(s: Session, tg_id: int) -> Iterable[PremiumRequest]:
    user = s.scalar(select(User).where(User.tg_id == tg_id))
    if not user:
        return []
    return s.scalars(
        select(PremiumRequest).where(PremiumRequest.user_id == user.id).order_by(PremiumRequest.id.desc())
    ).all()
