from __future__ import annotations

from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from app.config import settings

# -------------------- aiogram (бот) --------------------
router = Router(name="system")


@router.message(CommandStart())
async def cmd_start(message: types.Message) -> None:
    # HQ-профиль — НИКАКИХ клавиатур
    if settings.bot_profile == "hq":
        await message.answer("Привет! Я HQ-бот. Доступно: /status, /version, /panic.")
        return

    # trainer-профиль — простое меню без внешних зависимостей
    try:
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="🏋️ Тренировка дня"),
                    KeyboardButton(text="📈 Мой прогресс"),
                ],
                [
                    KeyboardButton(text="🎯 Путь лидера"),
                    KeyboardButton(text="⚙️ Настройки"),
                ],
                [KeyboardButton(text="⭐ Расширенная версия")],
            ],
            resize_keyboard=True,
        )
    except Exception:
        kb = None

    if kb:
        await message.answer("Меню тренировки:", reply_markup=kb)
    else:
        await message.answer("Меню тренировки активно.")


# -------------------- fastapi (веб) --------------------
# Небольшой JSON для автообновления панели: /ui/stats.json
# (подключается в main.py: `from app.routers.system import web_router as system_web_router`;
#  затем `app.include_router(system_web_router)` )
try:
    from fastapi import APIRouter
    from fastapi.responses import JSONResponse
    from app.core.store import get_scene_stats

    web_router = APIRouter()

    @web_router.get("/ui/stats.json")
    async def ui_stats():
        # компактный JSON: {"counts":{...}, "last_updated": "...", "last_reflection": "...", "ok": True}
        return JSONResponse(get_scene_stats() | {"ok": True})

except Exception:
    # Если FastAPI недоступен в среде — молча пропускаем веб-часть
    web_router = None  # type: ignore
