# app/sentry.py
from __future__ import annotations

import logging
import os

try:
    import sentry_sdk  # type: ignore
except Exception:  # sentry необязателен
    sentry_sdk = None  # type: ignore


def init_sentry(env: str, release: str) -> bool:
    """
    Инициализировать Sentry, если задан DSN.
    Возвращает True, если инициализация прошла, иначе False.
    """
    dsn = os.getenv("SENTRY_DSN", "").strip()
    if not dsn or sentry_sdk is None:
        logging.info("SENTRY: disabled (no DSN or package)")
        return False

    # Трейсы по умолчанию отключены; при желании можно поднять
    sentry_sdk.init(dsn=dsn, environment=env, release=release, traces_sample_rate=0.0)
    logging.info(f"SENTRY: initialized ✅ env={env} release={release}")
    return True


def capture_test_message() -> None:
    """
    Отправить тестовое сообщение в Sentry (удобно для проверки подключений).
    Безопасна к отсутствию пакета/DSN.
    """
    if sentry_sdk is None:
        return
    try:
        sentry_sdk.capture_message("Sentry test message from Elaya bot")
        logging.info("SENTRY: test message sent ✅")
    except Exception as e:  # на всякий
        logging.warning(f"SENTRY: test message failed: {e}")
