from __future__ import annotations

from aiogram import Router

from .training_flow import router as training_flow_router
from .menu import router as menu_router

# Корневой роутер тренера
router = Router(name="root")

# ВАЖНО: порядок подключения
# 1) FSM тренировки дня — всегда первой
router.include_router(training_flow_router)

# 2) Меню, навигация и служебные кнопки
router.include_router(menu_router)
