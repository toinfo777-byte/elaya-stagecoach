from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from app.build import BUILD_MARK

router = Router(name="system")

@router.message(CommandStart())
async def cmd_start(msg: Message):
    await msg.answer(
        "Команды и разделы: выбери нужное 🧭\n\n"
        "🏋️ Тренировка дня — ежедневная рутина 5–15 мин.\n"
        "📈 Мой прогресс — стрик и эпизоды за 7 дней.\n"
        "🎭 Мини-кастинг · 🧭 Путь лидера\n"
        "🆘 Помощь / FAQ · ⚙️ Настройки\n"
        "🔐 Политика · ⭐️ Расширенная версия"
    )

@router.message(Command("healthz"))
async def cmd_healthz(msg: Message):
    await msg.answer("ok")

@router.message(Command("getme"))
async def cmd_getme(msg: Message):
    me = await msg.bot.get_me()
    await msg.answer(f"id: <code>{me.id}</code>\nusername: @{me.username}\nbuild: <code>{BUILD_MARK}</code>")

# fallback на обычный текст — чтобы проверить, что апдейты доходят
@router.message(F.text)
async def echo_hint(msg: Message):
    # Ничего «не шумим» — только короткая подсказка на прямой текст
    if msg.text and msg.text.startswith("/"):
        return
    await msg.answer("Я здесь. Напиши /start или /status.")
