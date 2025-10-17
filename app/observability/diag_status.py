# app/observability/diag_status.py
from __future__ import annotations
import os
from .sentry import SENTRY_OK
from .health import CRONITOR_OK, LAST_PING_AT


def get_observe_status() -> dict:
    return {
        "env": os.getenv("ENV", "develop"),
        "release": os.getenv("SHORT_SHA", "local"),
        "sentry": "ok" if SENTRY_OK else "no_events",
        "cronitor": "ok" if CRONITOR_OK else "no_pulse",
        "render": "ok",   # если сервис жив — мы здесь
        "bot": "alive",   # доходит до хэндлера /diag
        "last_heartbeat_monotonic": LAST_PING_AT,
    }
