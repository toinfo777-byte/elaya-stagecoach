from __future__ import annotations
import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatType
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, BotCommand

from app.config import settings
from app.hq import build_hq_message

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("elaya.hq")

async def cmd_healthz(m: Message):
    await m.answer("pong 🟢")

async def cmd_hq(m: Message, command: CommandObject | None = None):
    # /hq — только текст сводки, без клавиатур
    await m.answer(build_hq_message())

async def cmd_start_private(m: Message):
    await m.answer(
        "Привет! Я HQ-бот Элайи.\n\n"
        "Доступные команды:\n"
        "• /hq — короткая техническая сводка\n"
        "• /healthz — проверка доступности"
    )

async def on_startup(bot: Bot):
    # Покажем список команд в клиенте
    await bot.set_my_commands(
        [
            BotCommand(command="hq", description="HQ-сводка"),
            BotCommand(command="healthz", description="Проверка доступности"),
            BotCommand(command="start", description="О боте"),
        ]
    )
    log.info("Bot started: env=%s mode=%s build=%s",
             settings.env, settings.mode, settings.build_mark)

def setup_routes(dp: Dispatcher):
    # Разрешаем /hq и /healthz в любом типе чатов (с privacy mode включенным
    # бот видит только команды и упоминания — это то, что нам нужно)
    dp.message.register(cmd_healthz, Command("healthz"))
    dp.message.register(cmd_hq,      Command("hq"))

    # /start — только в ЛС
    dp.message.register(
        cmd_start_private,
        Command("start"),
        F.chat.type == ChatType.PRIVATE
    )

async def main():
    bot = Bot(
        token=settings.token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    dp = Dispatcher()
    setup_routes(dp)
    dp.startup.register(on_startup)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
