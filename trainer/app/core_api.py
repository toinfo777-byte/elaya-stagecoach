# trainer/app/core_api.py
from __future__ import annotations
import os
import httpx

CORE_API_BASE = os.getenv("CORE_API_BASE", "").rstrip("/")
CORE_API_TOKEN = os.getenv("CORE_API_TOKEN", "")

_headers = {"X-Core-Token": CORE_API_TOKEN} if CORE_API_TOKEN else {}

class CoreAPIError(RuntimeError):
    pass

async def _post(path: str, payload: dict) -> dict:
    if not CORE_API_BASE:
        raise CoreAPIError("CORE_API_BASE is not set")
    url = f"{CORE_API_BASE}{path}"
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(url, headers=_headers, json=payload)
        try:
            data = r.json()
        except Exception:
            data = {"detail": r.text}
        if r.status_code >= 400:
            raise CoreAPIError(f"{r.status_code}: {data}")
        return data

async def scene_enter(user_id: int, chat_id: int, scene: str) -> str:
    data = await _post(
        "/api/scene/enter",
        {"user_id": user_id, "chat_id": chat_id, "scene": scene, "text": None},
    )
    return data.get("reply", "")

async def scene_reflect(user_id: int, chat_id: int, scene: str, text: str | None) -> str:
    data = await _post(
        "/api/scene/reflect",
        {"user_id": user_id, "chat_id": chat_id, "scene": scene, "text": text},
    )
    return data.get("reply", "")

async def scene_transition(user_id: int, chat_id: int, scene: str) -> str:
    data = await _post(
        "/api/scene/transition",
        {"user_id": user_id, "chat_id": chat_id, "scene": scene, "text": None},
    )
    return data.get("reply", "")
