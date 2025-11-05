from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from app.build import BUILD_MARK

router = Router(name="system")

@router.message(Command("healthz"))
async def cmd_healthz(msg: Message):
    await msg.answer("ok", reply_markup=ReplyKeyboardRemove())

@router.message(Command("help"))
async def cmd_help(msg: Message):
    await msg.answer(
        "HQ:\n"
        "• /status — статус ядра и билд\n"
        "• /webhookinfo — параметры вебхука\n"
        "• /healthz — быстрая проверка\n"
        "• /build — номер билда\n"
        "• /getme — инфо о боте\n"
        f"\nBuild: <code>{BUILD_MARK}</code>",
        reply_markup=ReplyKeyboardRemove()
    )
