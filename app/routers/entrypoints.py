from __future__ import annotations
from aiogram import Router, F
from aiogram.types import CallbackQuery

# единую менюшку рисуем в help.show_main_menu
from app.routers.help import show_main_menu

# если у тебя уже есть router = Router(...) — оставим его как есть,
# просто добавим обработчик ниже; либо используем отдельный go_router.
try:
    router  # noqa
    go_router = router
except NameError:
    go_router = Router(name="entrypoints")

# ВАЖНО: entrypoints перехватывает ВСЕ go:*
# Здесь мы забираем только go:menu (и совместимые ключи) и шлём в help.show_main_menu
@go_router.callback_query(F.data.in_({"go:menu", "to_menu", "core:menu"}))
async def ep_go_menu(cb: CallbackQuery):
    await show_main_menu(cb)

# Остальные go:* (go:training, go:leader, ...) остаются как у тебя реализованы
# в тематических роутерах — entrypoints их не трогает.
