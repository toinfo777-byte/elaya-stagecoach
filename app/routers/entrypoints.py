from __future__ import annotations
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from app.routers.help import show_main_menu

# используем имеющийся router, если он уже объявлен
try:
    router  # noqa: F821
    go_router = router
except NameError:
    go_router = Router(name="entrypoints")

# ВСЕ ВАРИАНТЫ «назад/в меню» уводим в help.show_main_menu
@go_router.callback_query(F.data.in_({"go:menu", "to_menu", "core:menu"}))
async def ep_cb_go_menu(cb: CallbackQuery):
    await show_main_menu(cb)

@go_router.message(F.text.in_({"В меню", "Меню", "🏠 В меню"}))
async def ep_txt_go_menu(m: Message):
    await show_main_menu(m)

# Остальные go:* роутинги (go:training/go:leader/...) оставьте как были.
