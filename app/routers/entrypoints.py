# app/routers/entrypoints.py
from __future__ import annotations
from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.ui.menu import show_main_menu

router = Router(name="entrypoints")

@router.callback_query(F.data == "go:menu")
async def go_menu(cb: CallbackQuery):
    await cb.answer(cache_time=1)
    await show_main_menu(cb)
