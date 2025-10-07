from __future__ import annotations
from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.routers.help import show_main_menu

try:
    router  # если у тебя уже есть router
    go_router = router
except NameError:
    go_router = Router(name="entrypoints")

@go_router.callback_query(F.data.in_({"go:menu", "to_menu", "core:menu"}))
async def ep_go_menu(cb: CallbackQuery):
    await show_main_menu(cb)
