# app/observability/__init__.py
from __future__ import annotations
import os
import logging

from .sentry import setup_sentry, capture_test_message


def setup_observability(*, env: str, release: str, send_test: bool = False) -> None:
    """
    Синхронная инициализация наблюдаемости, которую безопасно вызывать ДО старта event-loop.
    Сейчас включает только Sentry; heartbeat запускаем уже внутри running loop (см. main.py).
    """
    dsn = os.getenv("SENTRY_DSN", "").strip()
    ok = setup_sentry(dsn=dsn, env=env, release=release)
    if ok:
        logging.info("Sentry initialized (env=%s, release=%s)", env, release)
        if send_test:
            capture_test_message("Sentry init test ✓")
    else:
        logging.warning("Sentry DSN is empty — Sentry disabled")
