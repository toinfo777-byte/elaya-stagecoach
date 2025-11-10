from __future__ import annotations

import os
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/diag", tags=["diag"])

class WebhookInfo(BaseModel):
    profile: str
    env: str
    build: str
    guard_key: str  # первые 8 символов WEBHOOK_SECRET или пусто

@router.get("/ping")
def ping() -> dict[str, str]:
    return {"status": "ok"}

@router.get("/webhook", response_model=WebhookInfo)
def webhook_info() -> WebhookInfo:
    secret = os.getenv("WEBHOOK_SECRET", "")
    guard_key = secret[:8] if secret else ""
    return WebhookInfo(
        profile=os.getenv("BOT_PROFILE", "hq"),
        env=os.getenv("ENV", "unknown"),
        build=os.getenv("BUILD_MARK", "manual"),
        guard_key=guard_key,
    )
