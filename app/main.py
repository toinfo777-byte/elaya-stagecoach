# app/main.py
from __future__ import annotations

import asyncio
import inspect
import logging
import os
from typing import Any, Callable, Iterable

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeDefault,
)

# Единый источник /команд, если он у тебя есть. Иначе — безопасный заглушка.
try:
    from app.keyboards.menu import get_bot_commands  # type: ignore
except Exception:
    def get_bot_commands():
        return []

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("app.main")


# ============ УТИЛИТЫ ============
def _resolve_token() -> str:
    """Берём токен из app.config.settings или из ENV."""
    try:
        from app.config import settings  # type: ignore
    except Exception:
        settings = None  # noqa: N816

    candidates = ("BOT_TOKEN", "API_TOKEN", "TELEGRAM_TOKEN", "ELAYA_BOT_TOKEN")

    if settings is not None:
        for name in candidates:
            val = getattr(settings, name, None)
            if val:
                return val  # type: ignore[return-value]

    for name in candidates:
        val = os.getenv(name)
        if val:
            return val

    raise RuntimeError(
        "Bot token not found. Provide BOT_TOKEN (or API_TOKEN/TELEGRAM_TOKEN/ELAYA_BOT_TOKEN)."
    )


async def _maybe_await(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    if inspect.iscoroutinefunction(fn):
        return await fn(*args, **kwargs)
    return fn(*args, **kwargs)


async def _init_db_if_available() -> None:
    """Опциональный старт БД, если есть app.storage.repo.init_db"""
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


def _include_router_safe(dp: Dispatcher, dotted: str, attr: str = "router") -> bool:
    """Импортирует и включает роутер, если модуль есть. Возвращает True при успехе."""
    try:
        module = __import__(dotted, fromlist=[attr])
        router = getattr(module, attr)
        dp.include_router(router)
        log.info("Router included: %s.%s", dotted, attr)
        return True
    except Exception as e:
        log.warning("Skip router %s: %s", dotted, e)
        return False


def _include_router_try_both(
    dp: Dispatcher,
    module_name: str,
    prefixes: Iterable[str] = ("app.routers", "app.bot.routers"),
) -> None:
    """Пробуем подключить как app.routers.X и как app.bot.routers.X — что найдём, то подключим."""
    for base in prefixes:
        if _include_router_safe(dp, f"{base}.{module_name}"):
            return


async def _set_bot_commands_everywhere(bot: Bot) -> None:
    """Синхронизируем /команды (маленькое тг-меню) с нашим меню."""
    cmds = get_bot_commands()
    scopes = [
        BotCommandScopeDefault(),
        BotCommandScopeAllPrivateChats(),
        BotCommandScopeAllGroupChats(),
        BotCommandScopeAllChatAdministrators(),
    ]
    for sc in scopes:
        try:
            await bot.delete_my_commands(scope=sc)
        except Exception:
            pass
    for sc in scopes:
        try:
            await bot.set_my_commands(cmds, scope=sc)
        except Exception as e:
            log.warning("set_my_commands failed for %s: %s", sc, e)


# ============ MAIN ============
async def main() -> None:
    token = _resolve_token()
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()

    await _init_db_if_available()

    # Подключаем оба пространства имён
    for name in [
    # базовые служебные
    "system",
    "deeplink",         # если используешь deep link обработчики
    "cancel",           # если cancel вынесен в отдельный модуль

    # онбординг и сокращённые реплаи
    "onboarding",
    "reply_shortcuts",  # КНОПКИ «маленького меню»

    # основная логика
    "training",
    "casting",
    "progress",
    "apply",
    "premium",
    "privacy",
    "help",

    # отзывы/реакции
    "feedback",         # ЭМОДЗИ-ОЦЕНКИ и короткие фразы
    "shortcuts",        # если у тебя есть ещё общий модуль шорткатов
    "settings",
]:
    _include_router_try_both(dp, name)
    await _set_bot_commands_everywhere(bot)

    log.info("Bot is starting polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Bot stopped")
