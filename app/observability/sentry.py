from __future__ import annotations

import logging
import os

import sentry_sdk


def setup_sentry(*, env: str, release: str) -> bool:
    """
    Инициализирует Sentry, если задан DSN.
    Возвращает True, если Sentry включён.
    """
    dsn = (os.getenv("SENTRY_DSN") or "").strip()
    if not dsn:
        logging.info("Sentry: DSN пустой — мониторинг отключён.")
        return False

    traces = float(os.getenv("SENTRY_TRACES", "0") or 0)
    profiles = float(os.getenv("SENTRY_PROFILES", "0") or 0)

    sentry_sdk.init(
        dsn=dsn,
        environment=env,
        release=release,
        traces_sample_rate=traces,
        profiles_sample_rate=profiles,
    )
    logging.info("Sentry: инициализировано (env=%s, release=%s)", env, release)
    return True


def capture_test_message() -> None:
    sentry_sdk.capture_message("Sentry test message from Elaya bot")
