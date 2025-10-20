# app/control/utils.py
from __future__ import annotations

import os
import time
from datetime import timedelta

PROCESS_STARTED_AT = time.monotonic()

def uptime_str() -> str:
    td = timedelta(seconds=int(time.monotonic() - PROCESS_STARTED_AT))
    # h:mm:ss
    total = int(td.total_seconds())
    h, m = divmod(total, 3600)
    m, s = divmod(m, 60)
    return f"{h:d}h {m:02d}m {s:02d}s"

def env_or(name: str, default: str = "—") -> str:
    v = (os.getenv(name) or "").strip()
    return v or default
