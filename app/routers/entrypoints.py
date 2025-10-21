# app/routers/entrypoints.py
from __future__ import annotations
from aiogram import Router

# Подключаем готовые роутеры здесь
from .control import router as control_router  # /status, /report, /diag, ...

# Единая точка входа для всех роутеров бота
router = Router(name="entrypoints")
router.include_router(control_router)

__all__ = ["router"]
