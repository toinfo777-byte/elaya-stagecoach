# app/bot/routers/system.py
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

# наше постоянное нижнее меню
from app.bot.keyboards.menu import main_menu

# входные хендлеры разделов (мы зовём их напрямую)
from app.bot.routers.training import training_entry           # /training
from app.bot.routers.progress import progress_entry           # /progress
from app.bot.routers.apply import apply_entry                 # /apply
from app.bot.routers.casting import casting_entry             # /casting
from app.bot.routers.premium import premium_entry             # /premium
from app.bot.routers.settings import settings_entry           # /settings
from app.bot.routers.help import help_entry                   # /help
from app.bot.routers.privacy import privacy_entry             # /privacy

router = Router(name="system")


# ---------- базовые команды ----------
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    # даём онбординг как у тебя было
    await message.answer(
        "Привет! Я тренер «Школы театра Элайя». Соберём короткий профиль и начнём мини-тренировки.",
        reply_markup=main_menu(),
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Отменил текущее действие. Ты в меню.", reply_markup=main_menu())


# ---------- универсальный “выход из состояния + переход в раздел” ----------
async def _jump(message: Message, state: FSMContext, handler) -> None:
    """Сбрасываем любое состояние и запускаем указанный раздел."""
    await state.clear()
    await handler(message)


@router.message(Command("training"))
async def any_training(message: Message, state: FSMContext) -> None:
    await _jump(message, state, training_entry)


@router.message(Command("progress"))
async def any_progress(message: Message, state: FSMContext) -> None:
    await _jump(message, state, progress_entry)


@router.message(Command("apply"))
async def any_apply(message: Message, state: FSMContext) -> None:
    await _jump(message, state, apply_entry)


@router.message(Command("casting"))
async def any_casting(message: Message, state: FSMContext) -> None:
    await _jump(message, state, casting_entry)


@router.message(Command("premium"))
async def any_premium(message: Message, state: FSMContext) -> None:
    await _jump(message, state, premium_entry)


@router.message(Command("settings"))
async def any_settings(message: Message, state: FSMContext) -> None:
    await _jump(message, state, settings_entry)


@router.message(Command("help"))
async def any_help(message: Message, state: FSMContext) -> None:
    await _jump(message, state, help_entry)


@router.message(Command("privacy"))
async def any_privacy(message: Message, state: FSMContext) -> None:
    await _jump(message, state, privacy_entry)
