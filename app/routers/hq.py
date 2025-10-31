from __future__ import annotations

import os
from aiogram import Router, types
from aiogram.filters import Command

router = Router(name="hq")

def _render_info() -> dict:
    # мягко читаем переменные окружения — если чего-то нет, покажем «–»
    return {
        "Branch": os.getenv("RENDER_GIT_BRANCH", "–"),
        "Commit": os.getenv("RENDER_GIT_COMMIT", "–"),
        "Status": os.getenv("RENDER_SERVICE_STATUS", "–"),
        "Created": os.getenv("RENDER_SERVICE_CREATED_AT", "–"),
        "Updated": os.getenv("RENDER_SERVICE_UPDATED_AT", "–"),
    }

@router.message(Command("start"))
async def cmd_start(m: types.Message):
    text = (
        "Привет! Я HQ-бот Элайи.\n\n"
        "Доступные команды:\n"
        "• /hq — короткая техническая сводка\n"
        "• /healthz — проверка доступности\n"
        "• /menu — показать это меню"
    )
    await m.answer(text)

@router.message(Command("menu"))
async def cmd_menu(m: types.Message):
    await cmd_start(m)

@router.message(Command("healthz"))
async def cmd_healthz(m: types.Message):
    await m.answer("✅ ok")

@router.message(Command("hq"))
async def cmd_hq(m: types.Message):
    info = _render_info()
    lines = [
        "🧭 <b>Render Build</b>",
        f"• Branch: {info['Branch']}",
        f"• Commit: {info['Commit']}",
        f"• Status: {info['Status']}",
        f"• Created: {info['Created']}",
        f"• Updated: {info['Updated']}",
    ]
    # Подсказка, если не заведены ключи для Render API
    missing = []
    if not os.getenv("RENDER_API_KEY"):
        missing.append("RENDER_API_KEY")
    if not os.getenv("RENDER_SERVICE_ID"):
        missing.append("RENDER_SERVICE_ID")
    if missing:
        lines.append(f"\n⚠️ Не настроены {', '.join(missing)}.")
    await m.answer("\n".join(lines))
