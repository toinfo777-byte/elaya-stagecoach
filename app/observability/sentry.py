from __future__ import annotations

import logging
import os
import sentry_sdk

from .diag_status import mark_sentry_ok

def init_sentry(env: str, release: str) -> bool:
    """
    Инициализация Sentry.
    Возвращает True, если SDK реально активирован (есть DSN).
    """
    dsn = (os.getenv("SENTRY_DSN") or "").strip()
    if not dsn:
        logging.warning("Sentry: DSN not provided — SDK disabled")
        mark_sentry_ok(False)
        return False

    sentry_sdk.init(
        dsn=dsn,
        environment=env,
        release=release,
        traces_sample_rate=0.0,     # пока APM не включаем
        profiles_sample_rate=0.0,
        send_default_pii=False,
    )
    logging.info("Sentry: SDK initialized")
    mark_sentry_ok(True)
    return True


def capture_test_message() -> None:
    """
    Безопасный тест: просто сообщение (не ошибка).
    """
    try:
        sentry_sdk.capture_message("Sentry test message from Elaya bot")
    except Exception as e:
        logging.warning("Sentry capture_message failed: %s", e)
