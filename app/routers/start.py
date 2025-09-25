# app/routers/start.py
from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.filters.command import CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

router = Router(name="start")

# ✅ безопасные импорты входов (с алиасами на старые имена)
try:
    # если уже есть удобный вход
    from app.routers.training import training_entry  # type: ignore
except Exception:
    # fallback на основную функцию
    from app.routers.training import training_start as training_entry  # type: ignore

try:
    # удобный вход
    from app.routers.minicasting import minicasting_entry  # type: ignore
except Exception:
    # используем командный стартер (функцию можно вызывать напрямую)
    from app.routers.minicasting import start_minicasting_cmd as minicasting_entry  # type: ignore


@router.message(StateFilter("*"), CommandStart(deep_link=True))
async def start_deeplink(msg: Message, command: CommandObject, state: FSMContext):
    """Обрабатываем /start <payload>, например:
       ?start=go_training_post_2009  или  ?start=go_casting_post_2009
    """
    payload = (command.args or "").strip().lower()

    # Всегда сбрасываем состояние перед запуском сценария
    await state.clear()

    if payload.startswith("go_training"):
        return await training_entry(msg, state)

    if payload.startswith("go_casting"):
        return await minicasting_entry(msg, state)

    # Фолбэк — просто открываем меню
    from app.keyboards.reply import main_menu_kb
    await msg.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())


@router.message(StateFilter("*"), CommandStart())
async def start_plain(msg: Message, state: FSMContext):
    """Обычный /start без payload — приветствие + меню."""
    await state.clear()
    from app.keyboards.reply import main_menu_kb
    await msg.answer("Привет! Я Элайя — тренер сцены. Помогу прокачать голос и уверенность.")
    await msg.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())
