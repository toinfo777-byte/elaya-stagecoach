from __future__ import annotations
from aiogram import Router
from app.control.commands import router as control_router

router = Router(name="control_root")
router.include_router(control_router)
