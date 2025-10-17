# Простое зеркало состояния наблюдаемости

from __future__ import annotations
from typing import Dict

SENTRY_OK: bool = False
CRONITOR_OK: bool = False

def mark_sentry_ok(value: bool = True) -> None:
    global SENTRY_OK
    SENTRY_OK = value

def mark_cronitor_ok(value: bool = True) -> None:
    global CRONITOR_OK
    CRONITOR_OK = value

def get_observe_status() -> Dict[str, str]:
    return {
        "sentry":  "ok" if SENTRY_OK else "no_events",
        "cronitor": "ok" if CRONITOR_OK else "no_pulse",
        "render":  "ok",       # живём в Render, процесс ранится
        "bot":     "alive",    # запущен диспетчер
    }
