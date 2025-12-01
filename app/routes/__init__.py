# app/routes/__init__.py
from __future__ import annotations

from fastapi import APIRouter

from .system import router as system_router

router = APIRouter()

# только API ядра, без телеграм-меню
router.include_router(system_router)
