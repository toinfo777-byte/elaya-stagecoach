from __future__ import annotations
import logging

from .sentry import init_sentry, capture_test_message
from .health import start_healthcheck

def setup_observability(*, env: str, release: str, send_test: bool) -> None:
    """
    Синхронная часть наблюдаемости: только Sentry.
    ВАЖНО: heartbeat Cronitor НЕ запускаем здесь (цикла ещё нет).
    Его стартуй из уже работающего event loop (например, в main()).
    """
    sentry_enabled = init_sentry(env=env, release=release)
    if sentry_enabled and send_test:
        capture_test_message()
    logging.info("Observability: Sentry setup done (heartbeat will start inside event loop)")
