# app/build.py
from __future__ import annotations
import os
import subprocess

def _sh(cmd: str) -> str | None:
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return None

# короткий SHA
GIT_SHA = os.getenv("GIT_SHA") or _sh("git rev-parse --short HEAD") or "unknown"

# mark сборки: приоритет env -> Render commit -> просто SHA
BUILD_MARK = (
    os.getenv("BUILD_MARK")
    or os.getenv("RENDER_GIT_COMMIT", "")[:7]
    or GIT_SHA
)

# образ — если прокидываешь; иначе пусто (в отчёте это поле опционально)
IMAGE = os.getenv("IMAGE") or ""
ENV_NAME = os.getenv("ENV") or "develop"
