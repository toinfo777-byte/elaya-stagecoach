# app/routers/entrypoints.py
from __future__ import annotations
from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.routers.help import show_main_menu

go_router = Router(name="entrypoints")

@go_router.callback_query(F.data == "go:menu")
async def go_menu(cb: CallbackQuery):
    await cb.answer()
    await show_main_menu(cb.message)
