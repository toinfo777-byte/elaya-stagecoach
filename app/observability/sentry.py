# app/observability/sentry.py
from __future__ import annotations
import os
from typing import Optional
import sentry_sdk

def init_sentry(*, dsn: Optional[str], env: str = "prod", release: Optional[str] = None) -> None:
    """
    Инициализация Sentry. Без DSN — тихо выходим.
    traces_sample_rate=0.0 — отключаем перфоманс, оставляем только ошибки/сообщения.
    """
    if not dsn:
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=env,
        release=release,
        traces_sample_rate=0.0,
        send_default_pii=False,
    )

def capture_test_message():
    """Опционально: отправить тестовое событие, чтобы закрыть Sentry-мастер."""
    try:
        sentry_sdk.capture_message("✅ Sentry test message from Elaya bot")
    except Exception:
        pass
