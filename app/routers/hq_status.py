from __future__ import annotations
import time
import os
from fastapi import APIRouter

try:
    from app.build import BUILD_MARK
except Exception:
    BUILD_MARK = "unknown"

router = APIRouter()
_START_TS = time.time()

def _uptime_str() -> str:
    secs = int(time.time() - _START_TS)
    h, rem = divmod(secs, 3600)
    m, _ = divmod(rem, 60)
    return f"{h}h {m}m"

def _env(name: str, default: str) -> str:
    v = os.getenv(name)
    return v if v and v.strip() else default

@router.get("/status_json")
def status_json():
    return {
        "status_emoji": _env("HQ_STATUS_EMOJI", "🌞"),
        "status_word":  _env("HQ_STATUS_WORD",  "Stable"),
        "build":        _env("HQ_STATUS_BUILD", BUILD_MARK),
        "uptime":       _uptime_str(),
        "focus":        _env("HQ_STATUS_FOCUS", "Система в ритме дыхания"),
        "note":         _env("HQ_STATUS_NOTE",  "Web и Bot синхронны; пульс ровный."),
        "quote":        _env("HQ_STATUS_QUOTE", "«Ноябрь — дыхание изнутри.»"),
    }
