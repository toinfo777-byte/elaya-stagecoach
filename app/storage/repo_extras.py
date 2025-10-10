from __future__ import annotations
from typing import Any, Dict, Optional
import json
import logging
import asyncio

log = logging.getLogger(__name__)

__all__ = [
    "save_casting_session",
    "save_feedback",
    "log_progress_event",
    "save_leader_intent",
    "save_premium_request",
    "delete_user",
    "save_casting",
]


# === Вспомогательные функции ===
def _safe_dump(obj: Any) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except Exception:
        return str(obj)


# === Заглушки для событий ===
def save_casting_session(user_id: int, payload: Dict[str, Any]) -> None:
    """Мини-кастинг: сохраняем заявку (логируем вместо БД)."""
    log.info("save_casting_session(uid=%s): %s", user_id, _safe_dump(payload))


def save_feedback(
    user_id: int,
    text: str,
    rating: Optional[int] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    """Обратная связь пользователя."""
    log.info(
        "save_feedback(uid=%s): text=%r, rating=%s, meta=%s",
        user_id, text, rating, _safe_dump(meta),
    )


def log_progress_event(user_id: int, kind: str, data: Optional[Dict[str, Any]] = None) -> None:
    """Унифицированный лог прогресса/событий."""
    log.info("log_progress_event(uid=%s): kind=%s data=%s", user_id, kind, _safe_dump(data))


def save_leader_intent(user_id: int, intent: str, meta: Optional[Dict[str, Any]] = None) -> None:
    """Пользователь проявил интерес к «Пути лидера»."""
    log.info("save_leader_intent(uid=%s): intent=%s meta=%s", user_id, intent, _safe_dump(meta))


def save_premium_request(user_id: int, plan: str, meta: Optional[Dict[str, Any]] = None) -> None:
    """Запрос на премиум/расширенную версию."""
    log.info("save_premium_request(uid=%s): plan=%s meta=%s", user_id, plan, _safe_dump(meta))


# === Заглушка удаления пользователя ===
async def delete_user(user_id: int) -> None:
    """Асинхронная заглушка удаления пользователя по tg_id."""
    await asyncio.sleep(0)
    log.info("delete_user(uid=%s): stub OK", user_id)


# === Заглушка полной формы кастинга ===
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
    """Полный кастинг (анкета)."""
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
    log.info("save_casting(uid=%s): %s", tg_id, _safe_dump(payload))
