from __future__ import annotations

from aiogram import Router

from app.control.commands import router as control_router

# Единая точка подключения команд управления
router = Router(name="control-root")
router.include_router(control_router)
