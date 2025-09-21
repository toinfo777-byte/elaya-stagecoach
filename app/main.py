# app/main.py
from __future__ import annotations

import asyncio
import logging
from importlib import import_module

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

from app.config import settings
from app.storage.repo import ensure_schema

log = logging.getLogger("main")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)


def _try_import_router(module_path: str, router_name: str = "router"):
    """
    Пытаемся подключить роутер из модуля. Если модуля нет или в нём нет router — просто предупреждаем.
    """
    try:
        mod = import_module(module_path)
        router = getattr(mod, router_name)
        log.info("✅ Router '%s' подключён", module_path.rsplit(".", 1)[-1])
        return router
    except Exception as e:
        log.warning("Router '%s' NOT found — пропускаю (%s)", module_path.rsplit(".", 1)[-1], e)
        return None


async def _set_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="start", description="Начать / онбординг"),
        BotCommand(command="menu", description="Открыть меню"),
        BotCommand(command="training", description="Тренировка"),
        BotCommand(command="casting", description="Мини-кастинг"),
        BotCommand(command="progress", description="Мой прогресс"),
        BotCommand(command="apply", description="Путь лидера (заявка)"),
        BotCommand(command="privacy", description="Политика конфиденциальности"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="settings", description="Настройки"),
        BotCommand(command="cancel", description="Отмена"),
    ]
    await bot.set_my_commands(commands)
    log.info("✅ Команды установлены")


async def main() -> None:
    # 1) гарантируем схему БД (создаст таблицы, если их нет)
    ensure_schema()

    # 2) создаём бота (aiogram 3.7+ — parse_mode через DefaultBotProperties)
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )

    # убеждаемся, что webhook выключен (мы на long-polling)
    try:
        await bot.delete_webhook(drop_pending_updates=False)
    except Exception:
        # не критично
        pass

    dp = Dispatcher()

    # 3) Подключаем роутеры.
    # ВАЖНО: deeplink-роутеры (training/casting) подключаем ПЕРВЫМИ, чтобы обрабатывать /start с аргументами.
    for path in [
        "app.routers.training",         # deeplink на тренировки
        "app.routers.casting",          # deeplink на кастинг
        "app.routers.reply_shortcuts",  # кнопки "в меню" / "настройки" / "удалить профиль"
        "app.routers.cancel",           # /cancel
        "app.routers.onboarding",       # общий /start (после deeplink-роутеров!)
        "app.routers.menu",             # отображение меню
        "app.routers.apply",            # путь лидера
        "app.routers.progress",         # прогресс
        "app.routers.settings",         # настройки
        "app.routers.feedback",         # можно отсутствовать
        "app.routers.analytics",        # аналитика/health
    ]:
        r = _try_import_router(path)
        if r:
            dp.include_router(r)

    # 4) Команды
    await _set_commands(bot)

    log.info("🚀 Start polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
