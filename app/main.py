# app/main.py
from __future__ import annotations

import asyncio
import inspect
import logging
import os
from typing import Any, Callable

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeDefault,
)

from app.keyboards.menu import get_bot_commands  # единый источник /команд

# ===================== ЛОГГИ =====================
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("app.main")


# ===================== УТИЛИТЫ =====================
def _resolve_token() -> str:
    """
    Достаём токен из app.config.settings или из ENV.
    Поддерживаем несколько названий для совместимости.
    """
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
    """
    Опциональная инициализация БД, если в проекте есть app.storage.repo.init_db
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


def _include_router_safe(dp: Dispatcher, dotted: str, attr: str = "router") -> None:
    """
    Импортирует и включает роутер, если модуль существует.
    Не падает, если файла нет.
    """
    try:
        module = __import__(dotted, fromlist=[attr])
        router = getattr(module, attr)
        dp.include_router(router)
        log.info("Router included: %s.%s", dotted, attr)
    except Exception as e:
        log.warning("Skip router %s: %s", dotted, e)


async def _set_bot_commands_everywhere(bot: Bot) -> None:
    """
    Полностью синхронизируем /команды с нашим нижним меню.
    Это влияет на «маленькое меню» Telegram.
    """
    cmds = get_bot_commands()
    scopes = [
        BotCommandScopeDefault(),
        BotCommandScopeAllPrivateChats(),
        # на всякий случай очистим и для групповых скоупов
        BotCommandScopeAllGroupChats(),
        BotCommandScopeAllChatAdministrators(),
    ]

    # Сначала подчистим
    for sc in scopes:
        try:
            await bot.delete_my_commands(scope=sc)
        except Exception:
            pass

    # Затем выставим одинаковый набор
    for sc in scopes:
        try:
            await bot.set_my_commands(cmds, scope=sc)
        except Exception as e:
            log.warning("set_my_commands failed for %s: %s", sc, e)


# ===================== MAIN =====================
async def main() -> None:
    token = _resolve_token()
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()

    # Опционально — поднимем БД, если есть
    await _init_db_if_available()

    # Порядок подключения роутеров: шорткаты → онбординг → доменные → системные
    _include_router_safe(dp, "app.routers.shortcuts")
    _include_router_safe(dp, "app.routers.onboarding")
    _include_router_safe(dp, "app.routers.training")
    _include_router_safe(dp, "app.routers.casting")
    _include_router_safe(dp, "app.routers.progress")
    _include_router_safe(dp, "app.routers.apply")
    _include_router_safe(dp, "app.routers.system")
    _include_router_safe(dp, "app.routers.settings")
    _include_router_safe(dp, "app.routers.admin")
    _include_router_safe(dp, "app.routers.metrics")
    _include_router_safe(dp, "app.routers.analytics")
    _include_router_safe(dp, "app.routers.cancel")
    _include_router_safe(dp, "app.routers.feedback")
    _include_router_safe(dp, "app.routers.premium")  # <— ВАЖНО: расширенная версия

    # Ставим команды во всех скоупах
    await _set_bot_commands_everywhere(bot)

    log.info("Bot is starting polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Bot stopped")
