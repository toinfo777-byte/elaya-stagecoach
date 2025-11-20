from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
import os

import requests

from .config import CORE_URL, CORE_GUARD_KEY, CORE_TIMEOUT, APP_NAME, APP_VERSION


def is_configured() -> bool:
    """
    Есть ли web-core: проверяем, задан ли URL.
    """
    return bool(CORE_URL)


def _headers() -> Dict[str, str]:
    """
    Базовые заголовки для всех запросов к web-core.
    """
    headers: Dict[str, str] = {
        "User-Agent": f"{APP_NAME}-cli/{APP_VERSION}",
    }
    if CORE_GUARD_KEY:
        headers["X-Guard-Key"] = CORE_GUARD_KEY
    return headers


def _post_json(path: str, payload: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Вспомогательная функция: POST JSON в web-core.
    Возвращает (ok, error_message, json_response).
    """
    if not is_configured():
        return False, "CORE_URL is not configured (ELAYA_CORE_URL)", None

    url = CORE_URL + path
    try:
        response = requests.post(
            url,
            json=payload,
            headers=_headers(),
            timeout=CORE_TIMEOUT,
        )
        response.raise_for_status()
        try:
            data = response.json()
        except ValueError:
            data = None
        return True, None, data
    except Exception as exc:  # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}", None


def send_pulse(event: str, ok: bool = True, extra: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[str]]:
    """
    Отправляет событие в web-core (/api/pulse), если он настроен.
    """
    payload = {
        "event": event,
        "ok": ok,
        "extra": extra or {},
    }
    ok_flag, err, _ = _post_json("/api/pulse", payload)
    return ok_flag, err


def ping_core() -> Tuple[bool, str]:
    """
    Пробный запрос к web-core: /api/status.
    Используется командой `elaya3 sync`.
    """
    if not is_configured():
        return False, "ELAYA_CORE_URL не задан, web-core недоступен."

    url = CORE_URL + "/api/status"
    try:
        response = requests.get(  # type: ignore[call-arg]
            url,
            headers=_headers(),
            timeout=CORE_TIMEOUT,
        )
        response.raise_for_status()
        try:
            data = response.json()
        except ValueError:
            data = {}
        version = data.get("version", "?")
        return True, f"web-core online, version {version}"
    except Exception as exc:  # noqa: BLE001
        return False, f"Ошибка при запросе к web-core: {type(exc).__name__}: {exc}"
