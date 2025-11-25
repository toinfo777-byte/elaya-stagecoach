from __future__ import annotations

from fastapi import APIRouter

from . import api
from . import system
from . import ui

router = APIRouter()

# API ядра
router.include_router(api.router)

# системные /api эндпоинты
router.include_router(system.router)

# UI-страницы
router.include_router(ui.router)

__all__ = ["router"]
