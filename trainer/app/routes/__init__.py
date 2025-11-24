# trainer/app/routes/__init__.py
from __future__ import annotations

from aiogram import Router

from .menu import router as menu_router
from .training import router as training_router

router = Router(name="root")

# порядок важен только если где-то есть "заглушки" на все сообщения.
# У нас их нет, так что просто подключаем оба.
router.include_router(menu_router)
router.include_router(training_router)
