# app/storage/repo_extras.py
from __future__ import annotations

from typing import Any, Dict, Optional
import json
import logging

log = logging.getLogger(__name__)

__all__ = [
    "save_casting_session",
    "save_feedback",
    "log_progress_event",
    "save_leader_intent",
    "save_premium_request",
    "save_casting",
    "delete_user",
]

def _safe_dump(obj: Any) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except Exception:
        return str(obj)

# ===== Мини-кастинг (быстрые события) =====
def save_casting_session(user_id: int, payload: Dict[str, Any]) -> None:
    """Заглушка: логируем мини-кастинг."""
    log.info("save_casting_session(uid=%s): %s", user_id, _safe_dump(payload))

def save_feedback(
    user_id: int,
    text: str,
    rating: Optional[int] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    """Заглушка: обратная связь."""
    log.info(
        "save_feedback(uid=%s): text=%r, rating=%s, meta=%s",
        user_id, text, rating, _safe_dump(meta),
    )

def log_progress_event(user_id: int, kind: str, data: Optional[Dict[str, Any]] = None) -> None:
    """Заглушка: единый лог прогресса/событий."""
    log.info("log_progress_event(uid=%s): kind=%s data=%s", user_id, kind, _safe_dump(data))

# ===== Путь лидера / премиум =====
def save_leader_intent(user_id: int, intent: str, meta: Optional[Dict[str, Any]] = None) -> None:
    """Заглушка: интерес к «Пути лидера»."""
    log.info("save_leader_intent(uid=%s): intent=%s meta=%s", user_id, intent, _safe_dump(meta))

def save_premium_request(user_id: int, plan: str, meta: Optional[Dict[str, Any]] = None) -> None:
    """Заглушка: запрос на премиум."""
    log.info("save_premium_request(uid=%s): plan=%s meta=%s", user_id, plan, _safe_dump(meta))

# ===== Полный кастинг (длинная анкета) =====
def save_casting(
    *,
    tg_id: int,
    name: str,
    age: int,
    city: str,
    experience: str,
    contact: str,
    portfolio: Optional[str],
    agree_contact: bool,
) -> None:
    """Заглушка: полноценная анкета кастинга."""
    payload = {
        "tg_id": tg_id,
        "name": name,
        "age": age,
        "city": city,
        "experience": experience,
        "contact": contact,
        "portfolio": portfolio,
        "agree_contact": agree_contact,
    }
    log.info("save_casting: %s", _safe_dump(payload))

# ===== Сервисные заглушки =====
async def delete_user(tg_id: int) -> None:
    """Заглушка async-удаления пользователя по tg_id."""
    log.info("delete_user(uid=%s)", tg_id)
