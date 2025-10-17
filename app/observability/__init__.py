from __future__ import annotations

from .sentry import setup_sentry, capture_test_message
from .health import start_healthcheck


def setup_observability(*, env: str, release: str, send_test: bool = False) -> None:
    """
    Синхронная инициализация Sentry (и опциональный тест).
    Healthcheck-луп не трогаем здесь — его запускаем уже ВНУТРИ running loop.
    """
    ready = setup_sentry(env=env, release=release)
    if ready and send_test:
        capture_test_message()  # безопасное тест-сообщение
