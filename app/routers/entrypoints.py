from __future__ import annotations
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

# единое меню
from app.routers.help import show_main_menu, show_privacy, show_settings
# разделы
from app.routers.training import show_training_levels
from app.routers.progress import show_progress

# если в проекте уже объявлялся router — используем его; иначе создаём новый
try:
    router  # noqa: F821
    go_router = router
except NameError:
    go_router = Router(name="entrypoints")

# ───────────────────────────────────────────────────────────────────
# ВСЕ возвраты «в меню» (inline + текстовые) → единый экран из help
# ───────────────────────────────────────────────────────────────────
@go_router.callback_query(F.data.in_({"go:menu", "to_menu", "core:menu"}))
async def ep_cb_go_menu(cb: CallbackQuery):
    await show_main_menu(cb)

@go_router.message(F.text.in_({"В меню", "Меню", "🏠 В меню"}))
async def ep_txt_go_menu(m: Message):
    await show_main_menu(m)

# ───────────────────────────────────────────────────────────────────
# Кнопки верхнего инлайн-меню (go:*)
# ───────────────────────────────────────────────────────────────────
@go_router.callback_query(F.data == "go:training")
async def ep_training(cb: CallbackQuery):
    await cb.answer()
    await show_training_levels(cb.message, state=None)  # функция сама очистит state

@go_router.callback_query(F.data == "go:progress")
async def ep_progress(cb: CallbackQuery):
    await cb.answer()
    await show_progress(cb.message)

@go_router.callback_query(F.data == "go:help")
async def ep_help(cb: CallbackQuery):
    await cb.answer()
    await show_main_menu(cb)

@go_router.callback_query(F.data == "go:privacy")
async def ep_privacy(cb: CallbackQuery):
    await cb.answer()
    await show_privacy(cb)

@go_router.callback_query(F.data == "go:settings")
async def ep_settings(cb: CallbackQuery):
    await cb.answer()
    await show_settings(cb)

@go_router.callback_query(F.data == "go:extended")
async def ep_extended(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer("⭐ Расширенная версия: скоро тут будут доп. сценарии и метрики. ")
