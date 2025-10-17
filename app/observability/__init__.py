from __future__ import annotations
import logging

from .sentry import setup_sentry, capture_test_message


def setup_observability(*, env: str, release: str, send_test: bool = False) -> None:
    """
    Синхронная инициализация всего, что можно сделать до запуска event loop.
    Фоновый heartbeat запускаем в main() (внутри запущенного цикла).
    """
    enabled = setup_sentry(env=env, release=release)
    if enabled and send_test:
        capture_test_message()
        logging.info("Observability: sent test message to Sentry")
