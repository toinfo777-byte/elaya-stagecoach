from __future__ import annotations

from .sentry import SENTRY_OK
from .health import CRONITOR_OK

def get_observe_status() -> dict[str, str]:
    return {
        "sentry":   "ok" if SENTRY_OK else "no_events",
        "cronitor": "ok" if CRONITOR_OK else "no_pulse",
        "render":   "ok",      # если мы здесь — контейнер жив
        "bot":      "alive",   # если команда отрабатывает — цикл жив
    }
