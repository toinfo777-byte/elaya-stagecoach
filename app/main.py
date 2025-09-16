# app/main.py
from __future__ import annotations

import asyncio
import logging
import os
import inspect
from typing import Any, Callable

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

# === Настройки ================================================================
try:
    # ваш pydantic Settings
    from app.config import settings  # type: ignore
except Exception:  # запасной план — работаем только с ENV
    settings = None  # noqa: N816

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("app.main")


def _resolve_token() -> str:
    # 1) settings.BOT_TOKEN (приоритет)
    if settings is not None and getattr(settings, "BOT_TOKEN", None):
        return settings.BOT_TOKEN  # type: ignore[attr-defined]
    # 2) альтернативные имена в Settings (на всякий случай)
    for name in ("API_TOKEN", "TELEGRAM_TOKEN", "ELAYA_BOT_TOKEN"):
        if settings is not None and getattr(settings, name, None):
            return getattr(settings, name)  # type: ignore[no-any-return]
    # 3) переменные окружения
    for env_name in ("BOT_TOKEN", "API_TOKEN", "TELEGRAM_TOKEN", "ELAYA_BOT_TOKEN"):
        val = os.getenv(env_name)
        if val:
            return val
    raise RuntimeError(
        "Bot token not found. "
        "Provide BOT_TOKEN (or API_TOKEN/TELEGRAM_TOKEN/ELAYA_BOT_TOKEN) "
        "via app.config.settings or environment."
    )


async def _maybe_await(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Аккуратно вызвать sync/async функцию."""
    if inspect.iscoroutinefunction(fn):
        return await fn(*args, **kwargs)
    return fn(*args, **kwargs)


async def _init_db_if_available() -> None:
    """
    Мягкая инициализация БД:
    - если есть app.storage.repo.init_db – вызовем (sync/async);
    - если нет – только предупредим в логах, не падаем.
    """
    try:
        from app.storage.repo import init_db  # type: ignore
    except Exception:
        log.info("DB init: app.storage.repo.init_db not found – skipping.")
        return

    try:
        await _maybe_await(init_db)  # type: ignore[arg-type]
        log.info("DB init: OK")
    except Exception as e:
        log.exception("DB init failed: %s", e)


async def _set_bot_commands(bot: Bot) -> None:
    """Команды в левом меню Telegram. Дублируют главное меню / команды."""
    cmds = [
        BotCommand(command="menu", description="Открыть меню"),
        BotCommand(command="training", description="Тренировка дня"),
        BotCommand(command="progress", description="Мой прогресс"),
        BotCommand(command="casting", description="Мини-кастинг"),
        BotCommand(command="apply", description="Путь лидера (заявка)"),
        BotCommand(command="privacy", description="Политика конфиденциальности"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="version", description="Версия бота"),
        BotCommand(command="cancel", description="Сбросить состояние"),
    ]
    await bot.set_my_commands(cmds)


def _include_router_safe(dp: Dispatcher, dotted: str, attr: str = "router") -> None:
    """
    Безопасно подключить роутер: если нет файла/атрибута – просто предупреждение.
    dotted: строка модуля, напр. 'app.routers.training'
    attr:   имя экспортируемого объекта (по умолчанию 'router')
    """
    try:
        module = __import__(dotted, fromlist=[attr])
        router = getattr(module, attr)
        dp.include_router(router)
        log.info("Router included: %s.%s", dotted, attr)
    except Exception as e:
        log.warning("Skip router %s: %s", dotted, e)


async def main() -> None:
    # --- Бот и диспетчер
    token = _resolve_token()
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()

    # --- Инициализация БД (если доступна)
    await _init_db_if_available()

    # --- Подключаем роутеры.
    # Порядок важен: «шорткаты» и специальные — раньше, меню — строго последним.
    #
    # системные/пинговые (если есть)
    _include_router_safe(dp, "app.routers.smoke")

    # диплинки /start <payload> (если есть)
    _include_router_safe(dp, "app.routers.deeplink")

    # КОМАНДЫ/кнопки, которые должны работать в любом состоянии:
    _include_router_safe(dp, "app.routers.shortcuts")

    # онбординг (/start анкета)
    _include_router_safe(dp, "app.routers.onboarding")

    # доменные разделы
    _include_router_safe(dp, "app.routers.training")
    _include_router_safe(dp, "app.routers.casting")
    _include_router_safe(dp, "app.routers.progress")
    _include_router_safe(dp, "app.routers.apply")       # «Путь лидера» (заявка)

    # опциональные (если есть в проекте)
    _include_router_safe(dp, "app.routers.system")
    _include_router_safe(dp, "app.routers.settings")
    _include_router_safe(dp, "app.routers.admin")
    _include_router_safe(dp, "app.routers.metrics")
    _include_router_safe(dp, "app.routers.cancel")

    # ВАЖНО: роутер отзывов и премиума — чтобы кнопки работали всегда
    _include_router_safe(dp, "app.routers.feedback")
    _include_router_safe(dp, "app.routers.premium")

    # МЕНЮ — СТРОГО ПОСЛЕДНИМ
    _include_router_safe(dp, "app.routers.menu")

    # --- Команды в боковом меню
    await _set_bot_commands(bot)

    log.info("Bot is starting polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Bot stopped")
