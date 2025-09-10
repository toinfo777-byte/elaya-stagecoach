# app/routers/system.py
from __future__ import annotations
from datetime import datetime

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

router = Router(name="system")

# === ВЕРСИЯ RC ===
VERSION = "v0.7.0-rc1"  # <-- обновляй по мере выката

PRIVACY_TEXT = (
    "🔐 Политика конфиденциальности\n\n"
    "Мы храним минимальные данные, необходимые для работы бота: ваш Telegram ID, "
    "статус онбординга и результаты тренировок/кастинга. "
    "Данные не передаются третьим лицам и могут быть удалены по запросу (/wipe_me)."
)

HELP_TEXT = (
    "💬 Помощь\n\n"
    "Команды:\n"
    "/start — начать и онбординг\n"
    "/menu — открыть меню\n"
    "/apply — Путь лидера (заявка)\n"
    "/training — тренировка дня\n"
    "/casting — мини-кастинг\n"
    "/coach_on — включить наставника\n"
    "/coach_off — выключить наставника\n"
    "/ask <вопрос> — спросить наставника\n"
    "/progress — мой прогресс\n"
    "/cancel — сбросить состояние\n"
    "/privacy — политика конфиденциальности\n"
    "/version — версия бота\n"
    "/health — проверка статуса\n"
)

@router.message(StateFilter("*"), Command("help"))
async def help_cmd(m: Message):
    await m.answer(HELP_TEXT)

@router.message(StateFilter("*"), Command("privacy"))
async def privacy_cmd(m: Message):
    await m.answer(PRIVACY_TEXT)

@router.message(StateFilter("*"), Command("version"))
async def version_cmd(m: Message):
    await m.answer(f"Версия бота: *{VERSION}*", parse_mode="Markdown")

@router.message(StateFilter("*"), Command("health"))
async def health(m: Message):
    # быстрая проверка времени + echo id — этого достаточно для Render/RC
    await m.answer(f"OK {datetime.utcnow().isoformat(timespec='seconds')}Z")

@router.message(StateFilter("*"), Command("whoami"))
async def whoami(m: Message):
    u = m.from_user
    await m.answer(f"id: {u.id}\nusername: @{u.username or '—'}\nname: {u.full_name}")
