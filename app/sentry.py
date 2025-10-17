# app/sentry.py
from __future__ import annotations

import logging
import os
from typing import Any, Dict

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

SENTRY_OK: bool = False


def init_sentry(env: str, release: str) -> bool:
    """
    Инициализирует Sentry, если есть DSN. Возвращает True при успешной инициализации.
    """
    dsn = (os.getenv("SENTRY_DSN") or "").strip()
    if not dsn:
        logging.warning("Sentry DSN is empty — Sentry disabled")
        return False

    # Отправляем только ошибки (ERROR и выше) из логгера как события.
    logging_integration = LoggingIntegration(
        level=logging.INFO,
        event_level=logging.ERROR,
    )

    sentry_sdk.init(
        dsn=dsn,
        environment=env,
        release=release,
        integrations=[logging_integration],
        traces_sample_rate=0.0,  # трейсинг не нужен на этом этапе
    )

    global SENTRY_OK
    SENTRY_OK = True
    logging.info("✅ Sentry initialized")
    return True


def capture_test_message() -> None:
    """Однократный тест при старте (не в проде)."""
    if not SENTRY_OK:
        return
    sentry_sdk.capture_message("Sentry test message from Elaya bot")


def capture_message(msg: str, tags: Dict[str, Any] | None = None) -> None:
    """Безопасная отправка сообщения в Sentry с тегами."""
    if not SENTRY_OK:
        return
    with sentry_sdk.push_scope() as scope:
        for k, v in (tags or {}).items():
            scope.set_tag(k, v)
        sentry_sdk.capture_message(msg)


def capture_exception(exc: BaseException, tags: Dict[str, Any] | None = None) -> None:
    """Безопасная отправка исключения в Sentry с тегами."""
    if not SENTRY_OK:
        return
    with sentry_sdk.push_scope() as scope:
        for k, v in (tags or {}).items():
            scope.set_tag(k, v)
        sentry_sdk.capture_exception(exc)
