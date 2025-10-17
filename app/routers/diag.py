from __future__ import annotations

import os
from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import sentry_sdk

router = Router(name="diag")

# /version — показывает билд, окружение и время старта контейнера
@router.message(Command("version"))
async def cmd_version(msg: Message):
    release = os.getenv("SHORT_SHA", "local")
    env = os.getenv("ENV", "develop")
    # время старта процесса (примерно = времени билда/деплоя контейнера)
    started_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    await msg.answer(
        "<b>Elaya — Stagecoach | Dev</b>\n"
        f"🌿 <b>Environment:</b> <code>{env}</code>\n"
        f"🏗 <b>Release:</b> <code>{release}</code>\n"
        f"🕰 <b>Started at:</b> <code>{started_at}</code>"
    )

@router.message(Command("ping"))
async def cmd_ping(msg: Message):
    await msg.answer("pong 🟢")

@router.message(Command("health"))
async def cmd_health(msg: Message):
    await msg.answer("✅ Bot is alive and running!")

@router.message(Command("sentry_ping"))
async def cmd_sentry_ping(msg: Message):
    try:
        sentry_sdk.capture_message("✅ sentry: hello from elaya-stagecoach")
        await msg.answer("✅ Отправил тест-сообщение в Sentry")
    except Exception as e:
        await msg.answer(f"⚠️ Ошибка при отправке в Sentry: {e}")

@router.message(Command("boom"))
async def cmd_boom(msg: Message):
    await msg.answer("💣 Boom! Проверяем Sentry…")
    _ = 1 / 0  # намеренная ошибка
