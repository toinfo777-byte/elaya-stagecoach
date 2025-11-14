from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.filters.command import CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards.reply import main_menu_kb
from app.utils.core_client import core_event   # клиент CORE

router = Router(name="start")


# ============================================================
#               СТАРТ С ДИПЛИНКОМ
# ============================================================
@router.message(StateFilter("*"), CommandStart(deep_link=True))
async def start_with_deeplink(
    msg: Message,
    command: CommandObject,
    state: FSMContext
):
    payload = (command.args or "").strip().lower()

    # ---- старый диплинк: go_casting ----
    if payload.startswith("go_casting"):
        from app.routers.minicasting import start_minicasting
        await start_minicasting(msg, state)

        await core_event(
            source="bot",
            scene="start",
            payload={"deeplink": "go_casting"}
        )
        return

    # ---- старый диплинк: go_training ----
    if payload.startswith("go_training"):
        from app.routers.training import show_training_levels
        await show_training_levels(msg, state)

        await core_event(
            source="bot",
            scene="start",
            payload={"deeplink": "go_training"}
        )
        return

    # ---- новый формат диплинков ----
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


# ============================================================
#                     Обычный /start
# ============================================================
@router.message(StateFilter("*"), CommandStart())
async def plain_start(msg: Message, state: FSMContext):
    await state.clear()

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
