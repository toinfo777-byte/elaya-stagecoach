from __future__ import annotations
import os
from .sentry import init_sentry
from .health import boot_health

def setup_observability(*, env: str, release: str, send_test: bool = False) -> None:
    """
    Единая точка инициализации наблюдаемости.
    - Sentry (если задан DSN)
    - Health (лог метки старта)
    """
    dsn = os.getenv("SENTRY_DSN", "").strip()
    if dsn:
        init_sentry(env=env, release=release, send_test=send_test)
    boot_health(env=env, release=release)
