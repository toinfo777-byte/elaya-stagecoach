from __future__ import annotations

import asyncio
import importlib
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommandScopeAllPrivateChats

from app.config import settings
from app.keyboards.menu import get_bot_commands  # единый источник /команд

# === ЛОГИ =====================================================================
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "DEBUG"),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
log = logging.getLogger("main")

# === НАСТРОЙКИ ================================================================
BOT_TOKEN = settings.bot_token or os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Не найден BOT_TOKEN (settings.bot_token или ENV BOT_TOKEN).")

DATABASE_URL = settings.db_url or os.getenv("DATABASE_URL", "sqlite:///elaya.db")


# === ИМПОРТ РОУТЕРОВ ПО ИМЕНИ =================================================
def _import_router(module_base: str, name: str):
    candidates = [f"{module_base}.{name}", f"{module_base}.{name}.router"]
    for cand in candidates:
        try:
            mod = importlib.import_module(cand)
            if getattr(mod, "__class__", None).__name__ == "Router":
                return mod
            r = getattr(mod, "router", None)
            if r is not None:
                return r
        except Exception as e:
            logging.getLogger("import").debug("Import miss %s: %s", cand, e)
    return None


def _include(dp: Dispatcher, name: str):
    r = _import_router("app.routers", name)
    if not r:
        log.warning("Router '%s' NOT found — пропускаю", name)
        return False
    dp.include_router(r)
    log.info("✅ Router '%s' подключён", name)
    return True


async def _set_commands(bot: Bot):
    await bot.set_my_commands(get_bot_commands(), scope=BotCommandScopeAllPrivateChats())
    log.info("✅ Команды установлены")


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    # Подключаем ТОЛЬКО реально существующие роутеры (минимальный стабильный набор)
    routers = [
        "reply_shortcuts",   # «В меню», «Настройки», «Удалить профиль» и т.п. (reply)
        "cancel",
        "onboarding",        # весь /start (и deep-link) здесь
        "menu",              # хэндлеры нижнего меню и справки
        "training",
        "casting",
        "progress",
        "settings",
        "feedback",
        "analytics",
    ]
    for name in routers:
        _include(dp, name)

    return dp


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = build_dispatcher()
    await _set_commands(bot)

    log.info("🚀 Start polling…")
    await dp.start_polling(bot, allowed_updates=None)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Bot stopped.")
