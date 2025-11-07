# app/routers/diag.py
from __future__ import annotations

import os
from typing import Any, Dict

import httpx
from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.config import settings
from app.build import BUILD_MARK

router = APIRouter(prefix="/diag", tags=["diag"])


class WebhookInfo(BaseModel):
    url: str
    has_custom_certificate: bool
    pending_update_count: int
    ip_address: str | None = None
    max_connections: int | None = None


def _mask(s: str, keep: int = 4) -> str:
    if not s:
        return ""
    if len(s) <= keep * 2:
        return "*" * len(s)
    return s[:keep] + "…" + s[-keep:]


def _ok_guard(k: str | None) -> bool:
    """
    Примитивная защита от случайного публичного вызова:
    требуется ключ ?k=<первые 10 символов WEBHOOK_SECRET>.
    """
    if not settings.WEBHOOK_SECRET:
        return False
    expected = settings.WEBHOOK_SECRET[:10]
    return k == expected


@router.get("/webhook", summary="Статус Telegram webhook (диагностика)")
async def webhook_status(k: str | None = Query(default=None, description="guard key")) -> Dict[str, Any]:
    if not _ok_guard(k):
        return {"ok": False, "error": "forbidden"}

    tg_token = settings.TELEGRAM_TOKEN
    if not tg_token:
        return {"ok": False, "error": "TELEGRAM_TOKEN is empty"}

    api = f"https://api.telegram.org/bot{tg_token}/getWebhookInfo"

    async with httpx.AsyncClient(timeout=8.0) as client:
        r = await client.get(api)
        data = r.json()

    info_raw = data.get("result", {}) if isinstance(data, dict) else {}
    info = WebhookInfo.model_validate(info_raw)

    return {
        "ok": True,
        "service": {
            "build": BUILD_MARK,
            "profile": settings.BOT_PROFILE,
            "mode": os.getenv("MODE", ""),
            "env": settings.ENV,
            "render_service_id": os.getenv("RENDER_SERVICE_ID", ""),
        },
        "webhook": info.model_dump(),
        "checks": {
            "webhook_url_matches_render": (
                isinstance(info.url, str) and "onrender.com" in info.url
            ),
            "secret_configured": bool(settings.WEBHOOK_SECRET),
        },
        "secrets": {
            "TELEGRAM_TOKEN": _mask(tg_token),
            "WEBHOOK_SECRET": _mask(settings.WEBHOOK_SECRET or ""),
        },
    }


@router.get("/ping", summary="Быстрый пинг для liveness")
async def ping() -> Dict[str, str]:
    return {"status": "ok", "build": BUILD_MARK}
