from __future__ import annotations

from fastapi import APIRouter

from . import system
from . import ui
from . import api

# Корневой роутер ядра
router = APIRouter()

# системные /api эндпоинты (timeline, event, status и т.п.)
router.include_router(system.router)

# дополнительные API (пока пустой, но на будущее)
router.include_router(api.router)

# UI-страницы (если есть шаблоны)
router.include_router(ui.router)

__all__ = ["router"]
