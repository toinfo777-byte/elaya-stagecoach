# trainer/app/routes/__init__.py
from __future__ import annotations

from aiogram import Router

from . import menu
from . import training

router = Router(name="trainer-root")
router.include_router(menu.router)
router.include_router(training.router)
