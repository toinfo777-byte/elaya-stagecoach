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
    Делает SQLite-путь рабочим:
    - если путь относительный или каталог недоступен для записи — переносим в /tmp
    - создаём директорию, если её нет
    Остальные диалекты возвращаем как есть.
    """
    url: URL = make_url(raw)
    if url.get_backend_name() != "sqlite":
        return raw

    db_path = url.database or ""
    if db_path in ("", ":memory:"):
        return raw  # in-memory/пусто — ничего не делаем

    # абсолютный/относительный путь
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

    # если директория не пишется — используем /tmp
    if not _writable_dir(target_dir):
        log.warning("DB dir '%s' недоступна для записи. Переношу БД в /tmp", target_dir)
        base = os.path.basename(abs_path) or "elaya.db"
        abs_path = os.path.join("/tmp", base)
        os.makedirs("/tmp", exist_ok=True)

    # собрать итоговый URL
    fixed = url.set(database=abs_path)
    return str(fixed)

DB_URL = _resolve_db_url(settings.db_url)

# SQLite: никаких особых connect_args не нужно, оставим по умолчанию
engine = create_engine(DB_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)

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
    Dev-bootstrap: создаём отсутствующие таблицы.
    Безопасно для существующей схемы (ничего не трогает, если всё есть).
    """
    insp = inspect(engine)
    if not insp.has_table("users"):
        Base.metadata.create_all(bind=engine)
        log.info("✅ БД инициализирована (%s)", DB_URL)
