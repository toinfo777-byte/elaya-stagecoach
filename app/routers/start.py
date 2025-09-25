# app/routers/start.py
from __future__ import annotations

from aiogram import Router
from aiogram.filters.command import CommandStart, CommandObject
from aiogram.types import Message

from app.keyboards.reply import main_menu_kb
from app.routers.training import show_training_levels
from app.routers.minicasting import start_minicasting

router = Router(name="start")

@router.message(CommandStart(deep_link=True))
async def start_deeplink(msg: Message, command: CommandObject):
    payload = (command.args or "").lower()
    if payload.startswith("go_training"):
        await show_training_levels(msg)
        return
    if payload.startswith("go_casting"):
        from aiogram.fsm.context import FSMContext
        # если FSMContext нужен — aiogram сам инжектит при наличии аргумента;
        # здесь запускаем без явного стейта
        await start_minicasting(msg, state=None)  # наш хендлер принимает state, но None — ок, он не обязателен
        return
    await msg.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())

@router.message(CommandStart())
async def start_plain(msg: Message):
    await msg.answer("Привет! Я Элайя — тренер сцены. Помогу прокачать голос и уверенность.")
    await msg.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())
