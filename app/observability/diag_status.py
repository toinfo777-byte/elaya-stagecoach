from __future__ import annotations
from dataclasses import dataclass
from time import time

@dataclass
class ObserveState:
    sentry_ok: bool = False
    cronitor_ok: bool = False
    last_cronitor_ts: float | None = None

STATE = ObserveState()

def mark_sentry_ok() -> None:
    STATE.sentry_ok = True

def mark_cronitor_ok() -> None:
    STATE.cronitor_ok = True
    STATE.last_cronitor_ts = time()

def get_observe_status(env: str, release: str) -> dict:
    return {
        "env": env,
        "release": release,
        "sentry": "ok" if STATE.sentry_ok else "no_events",
        "cronitor": "ok" if STATE.cronitor_ok else "no_pulse",
        "render": "ok",
        "bot": "alive",
        "last_cronitor_ts": STATE.last_cronitor_ts,
    }
