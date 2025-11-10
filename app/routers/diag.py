# app/routers/diag.py
from __future__ import annotations

import os
import datetime as dt
from fastapi import APIRouter
from pydantic import BaseModel

# необязательные импорты: аккуратно пробуем дернуть store/BUILD_MARK,
# чтобы файл не падал, даже если их нет (на ранних коммитах).
try:
    from app.core import store  # type: ignore
except Exception:
    store = None  # noqa: N816  (дальше обрабатываем мягко)

try:
    from app.build import BUILD_MARK  # type: ignore
except Exception:
    BUILD_MARK = os.getenv("BUILD_MARK", "manual")

router = APIRouter(prefix="/diag", tags=["diag"])


class WebhookInfo(BaseModel):
    profile: str
    env: str
    build: str
    guard_key: str  # первые 8 символов WEBHOOK_SECRET или пусто


@router.get("/ping")
def ping() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/webhook", response_model=WebhookInfo)
def webhook_info() -> WebhookInfo:
    secret = os.getenv("WEBHOOK_SECRET", "") or ""
    return WebhookInfo(
        profile=os.getenv("BOT_PROFILE", "hq"),
        env=os.getenv("ENV", "unknown"),
        build=BUILD_MARK,
        guard_key=secret[:8] if secret else "",
    )


@router.get("/status_json")
def status_json() -> dict:
    """
    Лёгкий статус ядра. Все поля — best-effort:
    если чего-то нет/упало — возвращаем null/пусто, чтобы не ронять эндпоинт.
    """
    def _safe(callable_name: str, default=None):
        try:
            if store is None:
                return default
            fn = getattr(store, callable_name)
            return fn()
        except Exception:
            return default

    return {
        "ok": True,
        "updated": dt.datetime.utcnow().isoformat() + "Z",
        "build": BUILD_MARK,
        "env": os.getenv("ENV", "unknown"),
        "profile": os.getenv("BOT_PROFILE", "hq"),
        # ниже — опциональные штуки из store, если реализованы
        "scene_counts": _safe("count_scenes", {}),
        "last_scene": _safe("get_last_scene", None),
        "dup_guard": _safe("dup_seen_total", None),  # сколько дублей погашено
        "db_path": os.getenv("DB_PATH", "/data/elaya.db"),
    }
