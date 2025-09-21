# app/storage/repo.py
from __future__ import annotations

import os
import logging
from contextlib import contextmanager
from typing import Iterator
from datetime import date  # для type hints в async-методе

from sqlalchemy import create_engine, inspect, select  # select нужно для совместимости с вашим импортом
from sqlalchemy.engine.url import make_url, URL
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.storage.models import Base, async_session_maker, TrainingLog  # async фабрика и модель

log = logging.getLogger("db")


def _resolve_db_url(raw: str) -> str:
    """
    Чиним SQLite путь:
    - если каталог недоступен для записи — переносим файл в /tmp
    - создаём каталог при необходимости
    Для остальных диалектов возвращаем как есть.
    """
    url: URL = make_url(raw)
    if url.get_backend_name() != "sqlite":
        return raw

    db_path = url.database or ""
    if db_path in ("", ":memory:"):
        return raw

    abs_path = db_path if os.path.isabs(db_path) else os.path.abspath(db_path)
    target_dir = os.path.dirname(abs_path) or "."

    def _writable_dir(path: str) -> bool:
        try:
            os.makedirs(path, exist_ok=True)
            testfile = os.path.join(path, ".write_test")
            with open(testfile, "w") as f:
                f.write("ok")
            os.remove(testfile)
            return True
        except Exception:
            return False

    if not _writable_dir(target_dir):
        log.warning("DB dir '%s' недоступна для записи. Переношу БД в /tmp", target_dir)
        base = os.path.basename(abs_path) or "elaya.db"
        abs_path = os.path.join("/tmp", base)
        os.makedirs("/tmp", exist_ok=True)

    fixed = url.set(database=abs_path)
    return str(fixed)


DB_URL = _resolve_db_url(settings.db_url)

engine = create_engine(DB_URL, future=True)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
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


def ensure_schema() -> None:
    """
    Создаёт отсутствующие таблицы. Идемпотентно.
    """
    insp = inspect(engine)
    if not insp.has_table("users"):
        Base.metadata.create_all(bind=engine)
    log.info("✅ БД инициализирована (%s)", DB_URL)


# === Async repo API (для FSM-сценариев MVP) ==================================

async def repo_add_training_entry(user_id: int, day: date, level: str, done: bool):
    """
    Добавляет запись о тренировке пользователя.
    Использует async_session_maker и модель TrainingLog.
    """
    async with async_session_maker() as s:
        row = TrainingLog(user_id=user_id, day=day, level=level, done=done)
        s.add(row)
        await s.commit()
from __future__ import annotations

import os
import logging
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.url import make_url, URL
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.storage.models import Base

log = logging.getLogger("db")


def _resolve_db_url(raw: str) -> str:
    """
    Чиним SQLite путь:
    - если каталог недоступен для записи — переносим файл в /tmp
    - создаём каталог при необходимости
    Для остальных диалектов возвращаем как есть.
    """
    url: URL = make_url(raw)
    if url.get_backend_name() != "sqlite":
        return raw

    db_path = url.database or ""
    if db_path in ("", ":memory:"):
        return raw

    abs_path = db_path if os.path.isabs(db_path) else os.path.abspath(db_path)
    target_dir = os.path.dirname(abs_path) or "."

    def _writable_dir(path: str) -> bool:
        try:
            os.makedirs(path, exist_ok=True)
            testfile = os.path.join(path, ".write_test")
            with open(testfile, "w") as f:
                f.write("ok")
            os.remove(testfile)
            return True
        except Exception:
            return False

    if not _writable_dir(target_dir):
        log.warning("DB dir '%s' недоступна для записи. Переношу БД в /tmp", target_dir)
        base = os.path.basename(abs_path) or "elaya.db"
        abs_path = os.path.join("/tmp", base)
        os.makedirs("/tmp", exist_ok=True)

    fixed = url.set(database=abs_path)
    return str(fixed)


DB_URL = _resolve_db_url(settings.db_url)

engine = create_engine(DB_URL, future=True)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
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


def ensure_schema() -> None:
    """
    Создаёт отсутствующие таблицы. Идempotентно.
    """
    insp = inspect(engine)
    if not insp.has_table("users"):
        Base.metadata.create_all(bind=engine)
    log.info("✅ БД инициализирована (%s)", DB_URL)
