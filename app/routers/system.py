# app/routers/system.py
from __future__ import annotations
from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

router = Router(name="system")

# Экспортируемые константы (их ждёт menu.py)
PRIVACY_TEXT = (
    "🔐 Политика конфиденциальности\n\n"
    "Мы храним минимум данных, необходимые для работы бота: ваш Telegram ID, "
    "статус онбординга и результаты тренировок/кастинга. "
    "Данные не передаются третьим лицам и могут быть удалены по запросу."
)

HELP_TEXT = (
    "💬 Помощь\n\n"
    "Команды:\n"
    "/start — начать и онбординг\n"
    "/menu — открыть меню\n"
    "/apply — путь лидера (заявка)\n"
    "/training — тренировка дня\n"
    "/casting — мини-кастинг\n"
    "/coach_on — включить наставника\n"
    "/coach_off — выключить наставника\n"
    "/ask <вопрос> — спросить наставника\n"
    "/cancel — сбросить состояние\n"
    "/privacy — политика\n"
)

# Командные хендлеры доступны в любом состоянии
@router.message(StateFilter("*"), Command("help"))
async def help_cmd(m: Message):
    await m.answer(HELP_TEXT)

@router.message(StateFilter("*"), Command("privacy"))
async def privacy_cmd(m: Message):
    await m.answer(PRIVACY_TEXT)

# Опционально: быстрые техпинг/ктоя
@router.message(StateFilter("*"), Command("health"))
async def health(m: Message):
    await m.answer("OK")

@router.message(StateFilter("*"), Command("whoami"))
async def whoami(m: Message):
    u = m.from_user
    await m.answer(f"id: {u.id}\nusername: @{u.username or '—'}\nname: {u.full_name}")
