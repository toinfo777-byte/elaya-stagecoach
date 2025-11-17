from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.filters.command import CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards.reply import main_menu_kb
from app.utils.core_client import core_event  # клиент CORE

router = Router(name="start")


@router.message(StateFilter("*"), CommandStart())
async def start_entry(
    msg: Message,
    command: CommandObject | None,
    state: FSMContext,
):
    """
    Единая точка входа для /start:
    - без аргументов → обычный старт
    - ?start=go_casting → старый диплинк кастинга
    - ?start=go_training → старый диплинк тренировки
    - любые другие payload → просто фиксируем в CORE
    """

    # очищаем состояние для любого /start
    await state.clear()

    # достаём payload диплинка (если есть)
    payload = ""
    if command and command.args:
        payload = command.args.strip().lower()

    # ---- старый диплинк: go_casting ----
    if payload.startswith("go_casting"):
        from app.routers.minicasting import start_minicasting

        await start_minicasting(msg, state)
        await core_event(
            source="bot",
            scene="start",
            payload={"deeplink": "go_casting"},
        )
        return

    # ---- старый диплинк: go_training ----
    if payload.startswith("go_training"):
        from app.routers.training import show_training_levels

        await show_training_levels(msg, state)
        await core_event(
            source="bot",
            scene="start",
            payload={"deeplink": "go_training"},
        )
        return

    # ---- обычный /start (или неизвестный payload) ----
    await core_event(
        source="bot",
        scene="start",
        payload={
            "via": "deeplink" if payload else "command",
            "payload": payload or "-",
        },
    )

    await msg.answer(
        "Привет! Я Элайя — тренер сцены.\n"
        "Помогу прокачать голос, дыхание, уверенность и выразительность."
    )
    await msg.answer(
        "Готово! Открываю меню.",
        reply_markup=main_menu_kb(),
    )
