from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.reply import BTN_CASTING
from app.routers.minicasting import start_minicasting

router = Router(name="entrypoints")

# нижняя большая кнопка «🎭 Мини-кастинг» — из любого состояния
@router.message(StateFilter("*"), F.text == BTN_CASTING)
async def entry_minicasting_from_reply(m: Message, state: FSMContext):
    await start_minicasting(m, state)
