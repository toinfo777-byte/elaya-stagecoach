# app/routers/system.py
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.db import init_schema, read_state, save_reflection, bump_core

router = APIRouter(prefix="", tags=["system"])

# инициализируем БД при импортe роутера
init_schema()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def guard_ok(k: Optional[str]) -> bool:
    # защита тем же WEBHOOK_SECRET (достаточно первых 10 символов)
    guard = os.getenv("WEBHOOK_SECRET", "")
    return bool(k) and bool(guard) and guard.startswith(k)


# ── UI health ──────────────────────────────────────────────────────────────
@router.get("/ui/ping")
async def ui_ping():
    return {"ui": "ok"}


@router.get("/ui/stats.json")
async def ui_stats():
    state = read_state()
    payload: Dict[str, Any] = {
        "core": {
            "users": state["core"].get("users", 0),
            "intro": state["core"].get("intro", 0),
            "reflect": state["core"].get("reflect", 0),
            "transition": state["core"].get("transition", 0),
            "last_updated": state["core"].get("last_updated", ""),
        },
        "reflection": {
            "text": state["reflection"].get("text", ""),
            "updated_at": state["reflection"].get("updated_at", ""),
        },
        "status": "ok",
    }
    return JSONResponse(payload)


# ── Reflection сохранение (из UI) ─────────────────────────────────────────
@router.post("/ui/reflection/save")
async def ui_reflection_save(body: Dict[str, Any]):
    text = (body or {}).get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="empty text")

    save_reflection(text=text, updated_at=now_iso())
    # лёгкий «след» в core_state
    bump_core(delta_reflect=1, last_updated=now_iso())
    return {"ok": True}


# ── Телеметрия от trainer (безопасная) ─────────────────────────────────────
@router.post("/ui/telemetry/bump")
async def ui_telemetry_bump(request: Request, body: Dict[str, Any], k: Optional[str] = None):
    # приём guard из query ?k=... ИЛИ заголовка X-Guard
    if not guard_ok(k or request.headers.get("X-Guard")):
        raise HTTPException(status_code=403, detail="forbidden")

    d_users = int(body.get("users", 0) or 0)
    d_intro = int(body.get("intro", 0) or 0)
    d_reflect = int(body.get("reflect", 0) or 0)
    d_trans = int(body.get("transition", 0) or 0)

    bump_core(
        delta_users=d_users,
        delta_intro=d_intro,
        delta_reflect=d_reflect,
        delta_transition=d_trans,
        last_updated=now_iso(),
    )
    return {"ok": True}


# ── Диагностика ────────────────────────────────────────────────────────────
@router.get("/diag/ping")
async def diag_ping():
    return {"ok": True, "ts": now_iso()}


@router.get("/diag/webhook")
async def diag_webhook(k: Optional[str] = None):
    if not guard_ok(k):
        raise HTTPException(status_code=403, detail="forbidden")
    return {"ok": True, "ts": now_iso(), "webhook_guard_prefix_len": 10}


@router.get("/diag/env")
async def diag_env(k: Optional[str] = None):
    if not guard_ok(k):
        raise HTTPException(status_code=403, detail="forbidden")
    safe = {
        "SAFE_MODE": os.getenv("SAFE_MODE", "0"),
        "RENDER_SERVICE_ID": os.getenv("RENDER_SERVICE_ID", "-"),
        "STAGECOACH_WEB_URL": os.getenv("STAGECOACH_WEB_URL", "-"),
        "SQLITE_PATH": os.getenv("SQLITE_PATH", "/data/elaya.db"),
    }
    return JSONResponse(safe)
