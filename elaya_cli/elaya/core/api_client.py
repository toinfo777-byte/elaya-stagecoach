# elaya_cli/elaya/core/api_client.py

from __future__ import annotations

from typing import Any, Dict

import os
import requests

# Переменная окружения, откуда берём URL web-core
CORE_URL_ENV = "ELAYA_CORE_URL"

# Запасной URL по умолчанию (можешь поменять под себя)
DEFAULT_CORE_URL = "https://elaya-stagecoach-web.onrender.com"


def get_core_url() -> str:
    """
    Возвращает базовый URL web-core.

    1) Берём из переменной окружения E L A Y A _ C O R E _ U R L
    2) Если не задана — используем DEFAULT_CORE_URL.
    """
    base = os.getenv(CORE_URL_ENV, DEFAULT_CORE_URL).strip()
    if not base:
        base = DEFAULT_CORE_URL
    return base.rstrip("/")


def _core_url(path: str) -> str:
    """
    Строим полный URL до эндпоинта web-core.
    """
    return f"{get_core_url()}{path}"


def get_status() -> Dict[str, Any]:
    """
    Запрос состояния ядра: GET /api/status.

    Возвращает JSON как dict.
    """
    resp = requests.get(_core_url("/api/status"), timeout=10)
    resp.raise_for_status()
    return resp.json()


def send_event(source: str, scene: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Отправка произвольного события в web-core: POST /api/event.

    Аргументы:
      source — откуда пришло событие (например, "cli" или "bot")
      scene  — тип / сцена события ("manual", "intro", "reflect" и т.п.)
      payload — произвольный JSON-словарь с данными события

    Возвращает JSON ответ web-core (dict).
    """
    body = {
        "source": source,
        "scene": scene,
        "payload": payload,
    }
    resp = requests.post(_core_url("/api/event"), json=body, timeout=10)
    resp.raise_for_status()
    return resp.json()
