from __future__ import annotations
import os, time

START_TS = time.time()

def uptime_text() -> str:
    sec = int(time.time() - START_TS)
    d, rem = divmod(sec, 86400)
    h, rem = divmod(rem, 3600)
    m, _ = divmod(rem, 60)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    parts.append(f"{m}m")
    return " ".join(parts)

def build_mark() -> str:
    sha = (os.getenv("SHORT_SHA") or "local").strip() or "local"
    return sha[:7]

def env_name() -> str:
    return (os.getenv("ENV") or "develop").strip() or "develop"

def status_block() -> str:
    return (
        f"• ENV: <b>{env_name()}</b>\n"
        f"• BUILD: <code>{build_mark()}</code>\n"
        f"• Uptime: {uptime_text()}"
    )
