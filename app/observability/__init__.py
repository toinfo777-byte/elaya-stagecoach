from __future__ import annotations

import logging

from .sentry import init_sentry, capture_test_message
from .health import start_healthcheck


def init_observability(*, env: str, release: str, send_test: bool) -> None:
    """
    Централизованный вход: Sentry + Cronitor heartbeat.
    """
    sentry_enabled = init_sentry(env=env, release=release)
    if sentry_enabled and send_test:
        capture_test_message()

    task = start_healthcheck()
    if task:
        logging.info("Observability: heartbeat task started (%s)", task.get_name())
