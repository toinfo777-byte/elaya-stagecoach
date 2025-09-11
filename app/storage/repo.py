from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.engine.url import make_url

from app.config import settings
from app.storage.models import Base, User, Event


# 👇 ДОБАВЛЕНО: гарантируем, что папка для SQLite существует
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
