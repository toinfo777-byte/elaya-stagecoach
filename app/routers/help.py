# app/routers/help.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

# основной роутер раздела «Помощь»
help_router = Router(name="help")
# алиас для обратной совместимости (main.py делает r_help.router)
router = help_router


# ========= UI =========
def _menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏋️ Тренировка дня",   callback_data="go:training")],
        [InlineKeyboardButton(text="🎭 Мини-кастинг",     callback_data="go:casting")],
        [InlineKeyboardButton(text="🧭 Путь лидера",      callback_data="go:leader")],
        [InlineKeyboardButton(text="📈 Мой прогресс",     callback_data="go:progress")],
        [InlineKeyboardButton(text="🔐 Политика",         callback_data="go:privacy")],
        [InlineKeyboardButton(text="⚙️ Настройки",        callback_data="go:settings")],
    ])

def _back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")]
    ])


# единая функция ответа (Message | CallbackQuery)
async def _reply(obj: Message | CallbackQuery, text: str,
                 kb: InlineKeyboardMarkup | None = None):
    if isinstance(obj, CallbackQuery):
        await obj.answer()
        return await obj.message.answer(text, reply_markup=kb)
    return await obj.answer(text, reply_markup=kb)


# ========= ПУБЛИЧНЫЕ ФУНКЦИИ (их импортирует entrypoints.py) =========
async def show_main_menu(obj: Message | CallbackQuery):
    text = (
        "Команды и разделы: выбери нужное ⤵️\n\n"
        "🏋️ Тренировка дня — ежедневная рутина 5–15 мин.\n"
        "🎭 Мини-кастинг — быстрый чек 2–3 мин.\n"
        "🧭 Путь лидера — цель + микро-задание + заявка.\n"
        "📈 Мой прогресс — стрик и эпизоды за 7 дней.\n"
        "🔐 Политика — как храним и используем ваши данные.\n"
        "⚙️ Настройки — профиль/удаление.\n"
    )
    await _reply(obj, text, _menu_kb())

async def show_privacy(obj: Message | CallbackQuery):
    text = (
        "🔐 Политика конфиденциальности\n\n"
        "Мы бережно храним ваши данные и используем их только для работы бота.\n"
        "Удаление профиля доступно в ⚙️ Настройках."
    )
    await _reply(obj, text, _back_kb())

async def show_settings(obj: Message | CallbackQuery):
    text = (
        "⚙️ Настройки\n\n"
        "Здесь можно вернуться в меню или удалить профиль (кнопка появится в разделе настроек).\n"
        "Пока что — только возврат в меню."
    )
    await _reply(obj, text, _back_kb())


# ========= ХЭНДЛЕРЫ РАЗДЕЛА «ПОМОЩЬ» =========
@help_router.message(Command("help"))
async def _cmd_help(m: Message):
    await show_main_menu(m)

@help_router.callback_query(F.data == "go:menu")
async def _cb_menu(cb: CallbackQuery):
    await show_main_menu(cb)

@help_router.callback_query(F.data == "go:privacy")
async def _cb_privacy(cb: CallbackQuery):
    await show_privacy(cb)

@help_router.callback_query(F.data == "go:settings")
async def _cb_settings(cb: CallbackQuery):
    await show_settings(cb)


__all__ = [
    "help_router", "router",
    "show_main_menu", "show_privacy", "show_settings",
]
