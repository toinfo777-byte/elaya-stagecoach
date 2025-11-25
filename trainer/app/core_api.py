# trainer/app/core_api.py
from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx

CORE_API_BASE = (
    os.getenv("CORE_API_BASE", "")
    or os.getenv("CORE_URL", "")
    or os.getenv("CORE_BASE_URL", "")
    or os.getenv("TRAINER_CORE_URL", "")
).rstrip("/")

CORE_EVENTS_PATH = os.getenv("CORE_EVENTS_PATH", "/api/timeline")
GUARD_KEY = os.getenv("GUARD_KEY", "").strip()


async def send_timeline_event(
    scene: str,
    payload: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Асинхронная отправка события тренера в ядро Элайи.
    """

    if not CORE_API_BASE:
        print("[trainer→core] CORE_API_BASE is empty, skip event:", scene)
        return

    url = f"{CORE_API_BASE}{CORE_EVENTS_PATH}"

    headers: Dict[str, str] = {}
    if GUARD_KEY:
        headers["X-Guard-Key"] = GUARD_KEY

    data: Dict[str, Any] = {
        "source": "trainer",
        "scene": scene,
        "payload": payload or {},
    }

    # 🔍 Явный лог перед запросом
    print(f"[trainer→core] send event '{scene}' -> {url} | headers={headers} | data={data}")

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=data, headers=headers)
            print(f"[trainer→core] response status={resp.status_code}, body={resp.text!r}")
            resp.raise_for_status()
            print(f"[trainer→core] event sent OK: {scene}")
    except Exception as exc:
        print(f"[trainer→core] event error for scene '{scene}': {exc} | URL={url}")
