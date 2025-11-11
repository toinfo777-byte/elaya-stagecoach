from __future__ import annotations
import os
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import JSONResponse
from app.core import memory

router = APIRouter(prefix="", tags=["system"])

memory.init_db()

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def guard_key_ok(k: str | None) -> bool:
    guard = os.getenv("WEBHOOK_SECRET", "")
    return bool(k) and bool(guard) and guard.startswith(k)

# ─── UI ──────────────────────────────────────────────────────────────
@router.get("/ui/ping")
async def ui_ping():
    return {"ui": "ok"}

@router.get("/ui/stats.json")
async def ui_stats():
    stats = memory.get_stats()
    reflection = memory.last_reflection()
    return {
        "core": stats,
        "reflection": reflection,
        "status": "ok",
    }

@router.post("/ui/reflection/save")
async def ui_reflection_save(text: str = Form(...)):
    if not text.strip():
        raise HTTPException(status_code=400, detail="empty text")
    memory.save_reflection(text.strip())
    memory.update_stats("reflect")
    return {"ok": True, "saved": text.strip()}

# ─── DIAG ────────────────────────────────────────────────────────────
@router.get("/diag/ping")
async def diag_ping():
    return {"ok": True, "ts": _now_iso()}

@router.get("/diag/webhook")
async def diag_webhook(k: str | None = None):
    if not guard_key_ok(k):
        raise HTTPException(status_code=403, detail="forbidden")
    return {"ok": True, "ts": _now_iso()}
