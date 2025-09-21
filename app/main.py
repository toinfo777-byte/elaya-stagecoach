from __future__ import annotations

import asyncio
import importlib
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommandScopeAllPrivateChats

from app.config import settings
from app.keyboards.menu import get_bot_commands
from app.storage import repo as db  # <— модульный импорт, чтобы точно было

# Логи
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "DEBUG"),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
log = logging.getLogger("main")

BOT_TOKEN = settings.bot_token or os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Не найден BOT_TOKEN (settings.bot_token или ENV BOT_TOKEN).")


def _import_router(module_base: str, name: str):
    """
    Пробуем импортировать модуль и взять .router
    Поддерживаем варианты:
      app.routers.<name>
      app.routers.<name>.router  (если файл — пакет)
    """
    candidates = [f"{module_base}.{name}", f"{module_base}.{name}.router"]
    for cand in candidates:
        try:
            mod = importlib.import_module(cand)
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
    routers = [
        "reply_shortcuts",  # маленькое меню (В меню / Настройки / Удалить профиль)
        "cancel",           # общий /cancel (если есть)
        "onboarding",       # /start + диплинки
        "menu",             # кнопки главного меню
        "training",
        "casting",
        "apply",
        "progress",
        "settings",
        # "feedback",       # подключай, если модуль есть
        "analytics",        # если есть
    ]
    for name in routers:
        _include(dp, name)
    return dp


async def main():
    # 1) БД-инициализация (создаст отсутствующие таблицы)
    db.ensure_schema()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))

    # 2) На всякий случай снимем вебхук для long-poll
    try:
        await bot.delete_webhook(drop_pending_updates=False)
    except Exception as e:
        log.debug("delete_webhook skipped: %s", e)

    dp = build_dispatcher()
    await _set_commands(bot)

    log.info("🚀 Start polling…")
    await dp.start_polling(bot, allowed_updates=None)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Bot stopped.")
