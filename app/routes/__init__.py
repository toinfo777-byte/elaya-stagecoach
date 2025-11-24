# app/routes/__init__.py
from __future__ import annotations

from fastapi import APIRouter

from . import api
from . import system
from . import ui

router = APIRouter()

# API ядра (если используешь)
router.include_router(api.router)

# системные /api-эндпоинты (таймлайн и т.п.)
router.include_router(system.router)

# UI-страницы
router.include_router(ui.router)
