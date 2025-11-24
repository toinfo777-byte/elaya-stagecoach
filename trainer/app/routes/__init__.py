# trainer/app/routes/__init__.py
from __future__ import annotations

from aiogram import Router

from . import basic
from . import training

router = Router(name="root")

# порядок важен: сначала базовые вещи (/start и т.п.),
# потом — тренировка
router.include_router(basic.router)
router.include_router(training.router)
