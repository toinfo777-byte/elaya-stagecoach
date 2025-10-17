from __future__ import annotations
import logging
import os
from typing import Optional

import sentry_sdk

SENTRY_OK: bool = False   # станет True, когда успешно инициализируемся/пошлём событие


def setup_sentry(*, env: str, release: str) -> bool:
    """
    Инициализация Sentry по DSN из окружения.
    Возвращает True, если SDK включён.
    """
    dsn: Optional[str] = os.getenv("SENTRY_DSN") or os.getenv("SENTRY_DSN_URL")
    if not dsn:
        logging.info("Sentry: DSN not set — SDK disabled")
        return False

    sentry_sdk.init(
        dsn=dsn,
        environment=env,
        release=release,
        traces_sample_rate=float(os.getenv("SENTRY_TRACES", "0")),  # можно включить позже
        enable_db_queries=False,
    )
    logging.info("Sentry: SDK initialized (env=%s, release=%s)", env, release)
    global SENTRY_OK
    SENTRY_OK = True
    return True


def capture_test_message() -> None:
    """Безопасная тест-посылка, чтобы пометить SENTRY_OK."""
    try:
        sentry_sdk.capture_message("Sentry test message from Elaya bot")
        global SENTRY_OK
        SENTRY_OK = True
    except Exception as e:
        logging.warning("Sentry test send failed: %s", e)
