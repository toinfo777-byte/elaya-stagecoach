from __future__ import annotations
import os
from typing import Any, Dict, Optional

import httpx

# базовый URL ядра (web-сервис)
CORE_API_BASE = (
    os.getenv("CORE_API_BASE", "")
    or os.getenv("TRAINER_CORE_URL", "")
).rstrip("/")

CORE_EVENTS_PATH = "/api/timeline"

GUARD_KEY = (
    os.getenv("TRAINER_GUARD_KEY", "").strip()
    or os.getenv("GUARD_KEY", "").strip()
)


async def send_timeline_event(scene: str, payload: Optional[Dict[str, Any]] = None) -> None:
    """
    Отправка события тренера в ядро.
    """
    if not CORE_API_BASE:
        print("WARN: CORE_API_BASE не задан, событие не отправлено")
        return

    url = f"{CORE_API_BASE}{CORE_EVENTS_PATH}"

    headers = {}
    if GUARD_KEY:
        headers["X-Guard-Key"] = GUARD_KEY

    data = {
        "source": "trainer",
        "scene": scene,
        "payload": payload or {},
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=data, headers=headers)
            resp.raise_for_status()
            print(f"[OK] Trainer event → {scene}")
    except Exception as exc:
        print(f"[ERR] Trainer event error for {scene}: {exc}")
