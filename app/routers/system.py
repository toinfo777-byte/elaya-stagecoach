# app/routers/system.py
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

router = Router(name="system")

# Экспортируемые тексты — их использует меню
PRIVACY_TEXT = (
    "🔐 Политика конфиденциальности\n\n"
    "Мы храним минимальные данные, необходимые для работы бота: ваш Telegram ID, "
    "статус онбординга и результаты тренировок/кастинга. "
    "Ничего не передаём третьим лицам. Хотите удалить профиль и записи — команда /wipe_me."
)

HELP_TEXT = (
    "💬 Помощь\n\n"
    "Доступные команды:\n"
    "/start — начать и онбординг\n"
    "/menu — открыть меню\n"
    "/apply — подать заявку (Путь лидера)\n"
    "/training — тренировка дня\n"
    "/casting — мини-кастинг\n"
    "/coach_on — включить наставника\n"
    "/coach_off — выключить наставника\n"
    "/ask <вопрос> — спросить наставника\n"
    "/cancel — сбросить состояние и открыть меню\n"
    "/privacy — политика конфиденциальности\n"
)

# ===== Команды, доступные в любом состоянии =====
@router.message(StateFilter("*"), Command("help"))
async def help_cmd(m: Message):
    await m.answer(HELP_TEXT)

@router.message(StateFilter("*"), Command("privacy"))
async def privacy_cmd(m: Message):
    await m.answer(PRIVACY_TEXT)

# (опционально — техкоманды)
@router.message(StateFilter("*"), Command("health"))
async def health(m: Message):
    await m.answer("OK")

@router.message(StateFilter("*"), Command("whoami"))
async def whoami(m: Message):
    u = m.from_user
    await m.answer(f"id: {u.id}\nusername: @{u.username or '—'}\nname: {u.full_name}")
