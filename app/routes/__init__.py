# trainer/app/routes/__init__.py
from __future__ import annotations

from aiogram import Router

from .training_flow import router as training_flow_router
from .menu import router as menu_router

router = Router(name="root")

# ВАЖНО — порядок подключения:
# 1) FSM-тренировка
router.include_router(training_flow_router)

# 2) кнопки и меню
router.include_router(menu_router)
