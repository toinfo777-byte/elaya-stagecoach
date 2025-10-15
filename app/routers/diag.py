from aiogram import Router, F
from aiogram.types import Message
import sentry_sdk

router = Router(name="diag")

# === Базовые диагностические команды ===
@router.message(F.text.in_({"/ping", "ping"}))
async def cmd_ping(msg: Message):
    await msg.answer("pong 🟢")


@router.message(F.text.in_({"/health", "health"}))
async def cmd_health(msg: Message):
    await msg.answer("✅ Bot is alive and running!")


# === Тестовые команды для Sentry ===

@router.message(F.text.in_({"/sentry_ping", "sentry_ping"}))
async def cmd_sentry_ping(msg: Message):
    """
    Отправляет безопасное тестовое сообщение в Sentry.
    Можно использовать, чтобы проверить связь без падения бота.
    """
    try:
        sentry_sdk.capture_message("✅ sentry: hello from elaya-stagecoach")
        await msg.answer("✅ Отправил тест-сообщение в Sentry")
    except Exception as e:
        await msg.answer(f"⚠️ Ошибка при отправке в Sentry: {e}")


@router.message(F.text.in_({"/boom", "boom"}))
async def cmd_boom(msg: Message):
    """
    Намеренно вызывает исключение, чтобы проверить перехват Sentry.
    """
    await msg.answer("💣 Boom! Проверяем Sentry…")
    _ = 1 / 0  # сюда упадёт, и Sentry поймает RuntimeError
