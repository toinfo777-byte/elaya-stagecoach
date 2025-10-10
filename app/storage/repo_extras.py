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
    "delete_user",
]


def _safe_dump(obj: Any) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except Exception:
        return str(obj)


def save_casting_session(user_id: int, payload: Dict[str, Any]) -> None:
    """
    Заглушка для мини-кастинга.
    В проде здесь будет запись в БД. Пока просто логируем событие.
    """
    log.info("save_casting_session(uid=%s): %s", user_id, _safe_dump(payload))


def save_feedback(
    user_id: int,
    text: str,
    rating: Optional[int] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    """Заглушка для сохранения обратной связи пользователя."""
    log.info(
        "save_feedback(uid=%s): text=%r, rating=%s, meta=%s",
        user_id, text, rating, _safe_dump(meta),
    )


def log_progress_event(
    user_id: int,
    kind: str,
    data: Optional[Dict[str, Any]] = None,
) -> None:
    """Унифицированный лог прогресса/событий."""
    log.info("log_progress_event(uid=%s): kind=%s data=%s", user_id, kind, _safe_dump(data))


def save_leader_intent(
    user_id: int,
    intent: str,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    """Заглушка: пользователь проявил интерес к «Пути лидера»."""
    log.info("save_leader_intent(uid=%s): intent=%s meta=%s", user_id, intent, _safe_dump(meta))


def save_premium_request(
    user_id: int,
    plan: str,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    """Заглушка: запрос на премиум/расширенную версию."""
    log.info("save_premium_request(uid=%s): plan=%s meta=%s", user_id, plan, _safe_dump(meta))


# === Безопасная async-обёртка удаления профиля ===
async def delete_user(tg_id: int) -> None:
    """
    Пытаемся вызвать реальную async-функцию delete_user из app.storage.repo,
    если её нет — просто логируем, чтобы роутер не падал.
    """
    try:
        # импорт внутри функции, чтобы избежать циклических импортов
        from app.storage import repo  # type: ignore

        impl = getattr(repo, "delete_user", None)
        if impl is None:
            log.warning("repo.delete_user не найден; пропускаем удаление (uid=%s)", tg_id)
            return

        # если реализация синхронная — вызываем синхронно; если coroutine — await
        result = impl(tg_id)
        if hasattr(result, "__await__"):
            await result  # type: ignore[func-returns-value]
        else:
            # синхронная реализация
            pass

        log.info("delete_user: профиль удалён (uid=%s)", tg_id)
    except Exception as e:
        log.exception("delete_user: ошибка при удалении uid=%s: %s", tg_id, e)
        # прокидываем дальше, чтобы роутер мог показать «попробуй позже»
        raise
