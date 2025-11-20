from __future__ import annotations

import os
from typing import Any, Dict

import requests

# Базовый URL веб-ядра Элайи.
# Можно переопределить через переменную окружения ELAYA_WEB_URL.
BASE_URL = os.getenv(
    "ELAYA_WEB_URL",
    "https://elaya-stagecoach-web.onrender.com",
).rstrip("/")

# Таймаут запросов в секундах (можно задать через ELAYA_CLI_TIMEOUT).
TIMEOUT = float(os.getenv("ELAYA_CLI_TIMEOUT", "10"))


def _full_url(path: str) -> str:
    if not path.startswith("/"):
        path = "/" + path
    return f"{BASE_URL}{path}"


def get_core_status() -> Dict[str, Any]:
    """
    Получить статус ядра по /api/status.
    """
    resp = requests.get(_full_url("/api/status"), timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def send_event(source: str, scene: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Отправить событие в ядро по /api/event.
    """
    body = {
        "source": source,
        "scene": scene,
        "payload": payload,
    }
    resp = requests.post(_full_url("/api/event"), json=body, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()
