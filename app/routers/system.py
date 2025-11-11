from __future__ import annotations

from datetime import datetime, timezone
import os
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse

router = APIRouter(prefix="", tags=["system"])

# ── небольшое хранилище-пустышка (пока без БД) ─────────────────────────────────
STATE = {
    "core": {
        "users": 0,
        "intro": 0,
        "reflect": 0,
        "transition": 0,
        "last_updated": "",
    },
    "reflection": {"text": "", "updated_at": ""},
}

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ── UI / Ping / Stats ──────────────────────────────────────────────────────────
@router.get("/ui/ping")
async def ui_ping():
    return {"ui": "ok"}

@router.get("/ui/stats.json")
async def ui_stats():
    # отдаём «мок» (числа можно начнём брать уже из trainer позже)
    return {"core": STATE["core"], "reflection": STATE["reflection"], "status": "ok"}


# ── Диагностика вебхука бота ───────────────────────────────────────────────────
def guard_key_ok(k: str | None) -> bool:
    guard = os.getenv("WEBHOOK_SECRET", "")
    return bool(k) and bool(guard) and guard.startswith(k)  # первые 10 символов

@router.get("/diag/ping")
async def diag_ping():
    return {"ok": True, "ts": _now_iso()}

@router.get("/diag/webhook")
async def diag_webhook(k: str | None = None):
    if not guard_key_ok(k):
        raise HTTPException(status_code=403, detail="forbidden")
    # то, что можно безопасно показать
    return {
        "ok": True,
        "ts": _now_iso(),
        "webhook_guard_prefix_len": 10,
    }

# удобный text/plain, если нужно быстро посмотреть ключевую инфу с рендера
@router.get("/diag/env")
async def diag_env(k: str | None = None):
    if not guard_key_ok(k):
        raise HTTPException(status_code=403, detail="forbidden")
    safe = {
        "SAFE_MODE": os.getenv("SAFE_MODE", "0"),
        "RENDER_SERVICE_ID": os.getenv("RENDER_SERVICE_ID", "-"),
        "STAGECOACH_WEB_URL": os.getenv("STAGECOACH_WEB_URL", "-"),
    }
    return JSONResponse(safe)
