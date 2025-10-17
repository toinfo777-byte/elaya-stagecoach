from __future__ import annotations

import os
import time

# Момент старта процесса — для аптайма
PROCESS_STARTED_AT_MONO = time.monotonic()
PROCESS_STARTED_AT_UNIX = int(time.time())

# Маркеры окружения (используются в /status)
ENV = (os.getenv("ENV") or "develop").strip() or "develop"
RELEASE = (os.getenv("SHORT_SHA") or "local").strip() or "local"

__all__ = [
    "PROCESS_STARTED_AT_MONO",
    "PROCESS_STARTED_AT_UNIX",
    "ENV",
    "RELEASE",
]
