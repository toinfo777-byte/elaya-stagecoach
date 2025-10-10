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
    "save_leader_intent",
    "save_premium_request",
]

def _safe_dump(obj: Any) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except Exception:
        return str(obj)

# ==== minicasting ====

def save_casting_session(user_id: int, payload: Dict[str, Any]) -> None:
    """Заглушка: запись сессии мини-кастинга (лог)."""
    try:
        log.info("save_casting_session(uid=%s): %s", user_id, _safe_dump(payload))
    except Exception as e:
        log.exception("save_casting_session error: %s", e)

def save_feedback(
    user_id: int,
    text: str,
    rating: Optional[int] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    """Заглушка: сохранение обратной связи (лог)."""
    try:
        log.info(
            "save_feedback(uid=%s, rating=%s): %s | meta=%s",
            user_id, rating, text, _safe_dump(meta or {}),
        )
    except Exception as e:
        log.exception("save_feedback error: %s", e)

def log_progress_event(
    user_id: int,
    event: str,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    """Заглушка: лог события прогресса (лог)."""
    try:
        log.info(
            "log_progress_event(uid=%s) %s @ %s | meta=%s",
            user_id, event, datetime.utcnow().isoformat(timespec="seconds"),
            _safe_dump(meta or {}),
        )
    except Exception as e:
        log.exception("log_progress_event error: %s", e)

# ==== leader ====

def save_leader_intent(
    user_id: int,
    intent: str,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    """Заглушка: фиксация намерения лидера (лог)."""
    try:
        log.info(
            "save_leader_intent(uid=%s, intent=%s) meta=%s",
            user_id, intent, _safe_dump(meta or {}),
        )
    except Exception as e:
        log.exception("save_leader_intent error: %s", e)

def save_premium_request(
    user_id: int,
    plan: str,
    note: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    """Заглушка: запрос на премиум (лог)."""
    try:
        log.info(
            "save_premium_request(uid=%s, plan=%s, note=%s) meta=%s",
            user_id, plan, note, _safe_dump(meta or {}),
        )
    except Exception as e:
        log.exception("save_premium_request error: %s", e)
