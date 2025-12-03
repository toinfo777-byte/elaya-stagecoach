# app/routes/__init__.py
from __future__ import annotations

from fastapi import APIRouter

from .system import router as system_router

# Корневой роутер ядра
router = APIRouter()

# Подключаем только API-роутер ядра (таймлайн, прогресс и т.п.)
router.include_router(system_router)
