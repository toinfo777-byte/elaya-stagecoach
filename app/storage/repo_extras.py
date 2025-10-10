# app/storage/repo_extras.py
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

log = logging.getLogger("repo_extras")

__all__ = [
    "save_casting_session",
    "save_feedback",
    "log_progress_event",
]

def _safe_dump(obj: Any) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except Exception:
        return str(obj)

def save_casting_session(user_id: int, payload: Dict[str, Any]) -> None:
    """
    Совместимая заглушка для мини-кастинга.
    В прод-версии тут должна быть запись в БД. Сейчас просто логируем событие,
    чтобы не падал импорт и не рвались сценарии.
    """
    log.info("save_casting_session(uid=%s): %s", user_id, _safe_dump(payload))

def save_feedback(
    user_id: int,
    text: str,
    rating: Optional[int] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Совместимая заглушка для сохранения обратной связи.
    """
    log.info(
        "save_feedback(uid=%s, rating=%s): %s | meta=%s",
        user_id,
        rating,
        text,
        _safe_dump(meta or {}),
    )

def log_progress_event(
    user_id: int,
    event: str,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Совместимая заглушка для логирования прогресса/метрик.
    """
    log.info(
        "log_progress_event(uid=%s) %s @ %s | meta=%s",
        user_id,
        event,
        datetime.utcnow().isoformat(timespec="seconds"),
        _safe_dump(meta or {}),
    )
