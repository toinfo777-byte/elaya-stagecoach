from __future__ import annotations

from aiogram import Router, types
from aiogram.filters import CommandStart

from app.config import settings

router = Router(name="system")

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    if settings.bot_profile == "hq":
        # HQ: без клавиатур и меню
        await message.answer(
            "Привет! Я HQ-бот. Доступно: /status, /version, /panic."
        )
        return

    # TRAINER: показываем «фронтовое» меню
    # (здесь подключай свою реальную клавиатуру)
    # from app.ui.kb import trainer_menu_kb
    # await message.answer("Меню тренировки:", reply_markup=trainer_menu_kb())
    await message.answer("Меню тренировки:", reply_markup=None)  # временная заглушка
