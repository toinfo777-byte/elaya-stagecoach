from __future__ import annotations
from fastapi import APIRouter, Header, HTTPException
from datetime import datetime, timezone
from typing import Optional, List, Dict
import os

router = APIRouter(prefix="/api", tags=["api"])

GUARD_KEY = os.getenv("GUARD_KEY", "").strip()

timeline_events: List[Dict] = []   # простая память

def _check_guard(x_guard_key: Optional[str]):
    if not GUARD_KEY:
        return
    if (x_guard_key or "").strip() != GUARD_KEY:
        raise HTTPException(status_code=401, detail="invalid guard key")


@router.post("/timeline")
async def timeline_post(
    event: Dict,
    x_guard_key: Optional[str] = Header(None),
):
    _check_guard(x_guard_key)

    event["timestamp"] = datetime.now(timezone.utc).isoformat()
    timeline_events.append(event)

    return {"status": "ok"}


@router.get("/timeline")
async def timeline_get():
    return {"events": timeline_events}
