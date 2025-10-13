# app/storage/repo_extras.py
from __future__ import annotations

import logging
from typing import Any, Optional, Dict, List

log = logging.getLogger(__name__)

# ── Кастинг / миникастинг ─────────────────────────────────────────────────────

async def save_casting_session(
    *, user_id: int, answers: Optional[List[str]] = None, result: Optional[str] = None
) -> None:
    """Заглушка записи сессии мини-кастинга (no-op)."""
    log.info("repo_extras.save_casting_session [stub]: user_id=%s answers=%s result=%s",
             user_id, answers, result)

async def save_feedback(*, user_id: int, emoji: str, phrase: Optional[str]) -> None:
    """Заглушка записи фидбэка (no-op)."""
    log.info("repo_extras.save_feedback [stub]: user_id=%s emoji=%s phrase=%r",
             user_id, emoji, phrase)

async def log_progress_event(user_id: int, *, kind: str, meta: Optional[Dict[str, Any]] = None) -> None:
    """Заглушка логирования прогресса (no-op)."""
    log.info("repo_extras.log_progress_event [stub]: user_id=%s kind=%s meta=%s",
             user_id, kind, meta)

# ── Настройки / сервисные операции ────────────────────────────────────────────

async def delete_user(tg_id: int) -> None:
    """
    Заглушка удаления пользователя по tg_id (no-op).
    Ничего не удаляет — только пишет в лог, чтобы не падать.
    """
    log.warning("repo_extras.delete_user [stub]: tg_id=%s (no-op)", tg_id)

# ── Лидерский путь (чтобы заглушить редкие импорты) ───────────────────────────

async def save_leader_intent(*args, **kwargs) -> None:
    """Заглушка, если где-то ожидают save_leader_intent (no-op)."""
    log.info("repo_extras.save_leader_intent [stub]: args=%s kwargs=%s", args, kwargs)

__all__ = [
    "save_casting_session",
    "save_feedback",
    "log_progress_event",
    "delete_user",
    "save_leader_intent",
]
