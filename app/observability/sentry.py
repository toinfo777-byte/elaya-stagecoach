from __future__ import annotations
from typing import Optional
import os
import logging
import sentry_sdk

def init_sentry(*, dsn: Optional[str], env: str = "prod", release: Optional[str] = None) -> None:
    """
    Инициализация Sentry. Без DSN — выходим тихо.
    """
    if not dsn:
        logging.info("SENTRY: DSN not provided, skip init")
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=env,
        release=release,
        traces_sample_rate=0.0,   # метрики производительности отключены в dev
        send_default_pii=False,
    )
    logging.info(f"SENTRY: initialized ✅ env={env} release={release or 'n/a'}")

def capture_test_message() -> None:
    try:
        sentry_sdk.capture_message("Sentry test message from Elaya bot")
        logging.info("SENTRY: test message sent ✅")
    except Exception as e:
        logging.warning(f"SENTRY: test message failed: {e}")
