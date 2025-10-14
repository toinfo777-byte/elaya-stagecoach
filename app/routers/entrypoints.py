# app/routers/entrypoints.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from app.routers.help import show_main_menu

router = Router(name="entrypoints")
__all__ = ["router"]

# /menu и "menu" (на всякий случай)
@router.message(F.text.in_({"/menu", "menu"}))
async def cmd_menu(m: Message):
    await show_main_menu(m)

# Кнопка "домой" из инлайн-клавиатур
@router.callback_query(F.data == "go:menu")
async def go_menu(cb: CallbackQuery):
    await cb.answer()
    await show_main_menu(cb.message)

# Back-compat: чтобы старые импорты не падали
go_router = router
