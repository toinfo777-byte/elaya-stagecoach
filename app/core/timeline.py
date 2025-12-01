from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List

# Папка для данных ядра: app/data/timeline.json
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

TIMELINE_PATH = DATA_DIR / "timeline.json"
_LOCK = Lock()


def _load_events() -> List[Dict[str, Any]]:
    """
    Читает все события из файла.
    Если файла нет или формат битый — возвращает пустой список.
    """
    if not TIMELINE_PATH.exists():
        return []

    try:
        with TIMELINE_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except Exception:
        return []

    return []


def _save_events(events: List[Dict[str, Any]]) -> None:
    """
    Перезаписывает файл таймлайна.
    """
    with TIMELINE_PATH.open("w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)


def add_event(
    source: str,
    scene: str,
    payload: Dict[str, Any] | None = None,
    ts=None,
) -> Dict[str, Any]:
    """
    Добавляет событие в таймлайн и возвращает его.

    Параметр ts добавлен для совместимости с внешними клиентами (Trainer/CLI),
    но необязателен — ядро само поставит время, если ts не передан.
    """
    # если ts передан — нормализуем
    if ts is None:
        ts_str = datetime.now(timezone.utc).isoformat()
    else:
        # ts может быть datetime или строкой
        try:
            ts_str = ts.isoformat()
        except AttributeError:
            ts_str = str(ts)

    event: Dict[str, Any] = {
        "ts": ts_str,
        "source": source,
        "scene": scene,
        "payload": payload or {},
    }

    with _LOCK:
        events = _load_events()
        events.append(event)
        _save_events(events)

    return event


def get_timeline(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Возвращает последние N событий (по умолчанию 100), в хронологическом порядке.
    """
    with _LOCK:
        events = _load_events()

    if limit and limit > 0:
        return events[-limit:]
    return events
