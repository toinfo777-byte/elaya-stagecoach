from __future__ import annotations
from aiogram import Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message
from aiogram.filters.command import CommandObject
from app.keyboards.reply import main_menu_kb

router = Router(name="start")

@router.message(StateFilter("*"), CommandStart(deep_link=True))
async def start_deeplink(m: Message, command: CommandObject, state):
    await state.clear()
    payload = (command.args or "").lower()
    if payload.startswith("go_training") or payload.startswith("go:training"):
        try:
            from app.routers.training import training_start
            return await training_start(m, state)
        except Exception:
            pass
    if payload.startswith("go_casting") or payload.startswith("go:casting"):
        try:
            from app.routers.minicasting import start_minicasting
            return await start_minicasting(m, state)
        except Exception:
            pass
    if payload.startswith("go_apply") or payload.startswith("go:apply"):
        try:
            from app.routers.leader import leader_entry
            return await leader_entry(m, state)
        except Exception:
            pass
    await m.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())
