from __future__ import annotations
import os

def _parse_int(s: str) -> int | None:
    s = (s or "").strip()
    if not s or not s.lstrip("-").isdigit():
        return None
    try:
        return int(s)
    except Exception:
        return None

def _parse_ids_csv(raw: str | None) -> set[int]:
    if not raw:
        return set()
    ids: set[int] = set()
    for piece in raw.split(","):
        v = _parse_int(piece)
        if v is not None:
            ids.add(v)
    return ids

# Разрешённые админы (кто может вызывать команды управления)
_ADMIN_IDS: set[int] = _parse_ids_csv(os.getenv("ADMIN_IDS"))

# Куда слать алерты (дополнительно к админам)
_ALERT_CHAT_ID = _parse_int(os.getenv("ADMIN_ALERT_CHAT_ID"))

def admin_ids() -> set[int]:
    """Множество id пользователей-админов."""
    # если ADMIN_IDS не задан, но есть ALERT_CHAT_ID (личка) — считаем его тоже админом
    ids = set(_ADMIN_IDS)
    if _ALERT_CHAT_ID is not None:
        ids.add(_ALERT_CHAT_ID)
    return ids

def alert_targets() -> set[int]:
    """Куда рассылать уведомления (/notify_admins)."""
    targets = set(_ADMIN_IDS)
    if _ALERT_CHAT_ID is not None:
        targets.add(_ALERT_CHAT_ID)
    return targets

def is_admin(user_id: int | None) -> bool:
    return bool(user_id is not None and user_id in admin_ids())

class NotAdminError(PermissionError):
    pass

def require_admin(user_id: int | None) -> None:
    if not is_admin(user_id):
        raise NotAdminError("not-allowed")
