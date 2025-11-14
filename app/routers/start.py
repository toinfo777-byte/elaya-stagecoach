from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.filters.command import CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards.reply import main_menu_kb
from app.utils.core_client import core_event   # <-- новый клиент CORE

router = Router(name="start")


# --- универсальный запуск через диплинки ---
@router.message(StateFilter("*"), CommandStart(deep_link=True))
async def start_with_deeplink(msg: Message, command: CommandObject, state: FSMContext):
    payload = (command.args or "").strip().lower()

    # ---- старые диплинки ----
    if payload.startswith("go_casting"):
        from app.routers.minicasting import start_minicasting
        await start_minicasting(msg, state)

        # фиксируем событие
        await core_event(
            source="bot",
            scene="start",
            payload={"deeplink": "go_casting"}
        )
        return

    if payload.startswith("go_training"):
        from app.routers.training import show_training_levels
        await show_training_levels(msg, state)

        await core_event(
            source="bot",
            scene="start",
            payload={"deeplink": "go_training"}
        )
        return

    # ---- обычный старт через диплинк ----
    await state.clear()

    await core_event(
        source="bot",
        scene="start",
        payload={"deeplink": payload or "-"}
    )

    await msg.answer(
        "Привет! Я Элайя — тренер сцены.\n"
        "Помогу прокачать голос, дыхание, уверенность и выразительность."
    )
    await msg.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())


# --- обычный старт /start ---
@router.message(StateFilter("*"), CommandStart())
async def plain_start(msg: Message, state: FSMContext):
    await state.clear()

    # --- логируем старт в CORE ---
    await core_event(
        source="bot",
        scene="start",
        payload={"via": "command"}
    )

    await msg.answer(
        "Привет! Я Элайя — тренер сцены.\n"
        "Помогу прокачать голос, дыхание, уверенность и выразительность."
    )
    await msg.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())
