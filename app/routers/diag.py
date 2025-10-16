from aiogram import Router, F
from aiogram.types import Message
import sentry_sdk
import os

router = Router(name="diag")

ADMINS = {  # TG user_id админов
    538431234,  # пример
}

@router.message(F.text.in_({"/ping", "ping"}))
async def cmd_ping(msg: Message):
    await msg.answer("pong 🟢")

@router.message(F.text.in_({"/health", "health"}))
async def cmd_health(msg: Message):
    await msg.answer("✅ Bot is alive and running!")

@router.message(F.text.in_({"/sentry_ping", "sentry_ping"}))
async def cmd_sentry_ping(msg: Message):
    # богаче контекст: кто/где, сборка, окружение
    with sentry_sdk.push_scope() as scope:
        scope.set_user({"id": msg.from_user.id, "username": msg.from_user.username})
        scope.set_context("chat", {"id": msg.chat.id, "type": msg.chat.type})
        scope.set_tag("build", os.getenv("SHORT_SHA") or "local")
        scope.set_tag("env", os.getenv("ENV", "prod"))
        sentry_sdk.capture_message("✅ sentry: hello from elaya-stagecoach")
    await msg.answer("✅ Отправил тест-сообщение в Sentry")

@router.message(F.text.in_({"/boom", "boom"}))
async def cmd_boom(msg: Message):
    if msg.from_user.id not in ADMINS:
        await msg.answer("⛔ Команда доступна только администраторам.")
        return
    await msg.answer("💣 Boom! Проверяем Sentry…")
    _ = 1 / 0  # намеренный крэш
