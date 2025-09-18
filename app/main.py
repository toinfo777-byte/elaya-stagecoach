# app/main.py
from __future__ import annotations

import asyncio
import logging
import os
import inspect
from typing import Any, Callable

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    BotCommandScopeDefault,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllChatAdministrators,
)

# ⬇️ добавим импорт asyncpg
import asyncpg

from app.keyboards.menu import get_bot_commands  # единый источник /команд

# === Настройки ================================================================
try:
    from app.config import settings  # type: ignore
except Exception:
    settings = None  # noqa: N816

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("app.main")


def _resolve_token() -> str:
    if settings is not None and getattr(settings, "BOT_TOKEN", None):
        return settings.BOT_TOKEN  # type: ignore[attr-defined]
    for name in ("API_TOKEN", "TELEGRAM_TOKEN", "ELAYA_BOT_TOKEN"):
        if settings is not None and getattr(settings, name, None):
            return getattr(settings, name)  # type: ignore[no-any-return]
    for env_name in ("BOT_TOKEN", "API_TOKEN", "TELEGRAM_TOKEN", "ELAYA_BOT_TOKEN"):
        val = os.getenv(env_name)
        if val:
            return val
    raise RuntimeError("Bot token not found. Provide BOT_TOKEN (or API_TOKEN/TELEGRAM_TOKEN/ELAYA_BOT_TOKEN).")


async def _maybe_await(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    if inspect.iscoroutinefunction(fn):
        return await fn(*args, **kwargs)
    return fn(*args, **kwargs)


async def _init_db_if_available() -> None:
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

# ⬇️ НОВОЕ: создаём пул к БД, если есть DB_URL
async def _create_db_pool_if_possible(bot: Bot) -> None:
    dsn = (
        getattr(settings, "DB_URL", None)
        if settings is not None
        else None
    ) or os.getenv("DB_URL")
    if not dsn:
        log.info("DB_URL is not set – skipping pool creation.")
        return
    try:
        pool = await asyncpg.create_pool(dsn=dsn, min_size=1, max_size=10)
        bot["db_pool"] = pool
        log.info("DB pool created.")
    except Exception as e:
        log.exception("DB pool create failed: %s", e)


def _include_router_safe(dp: Dispatcher, dotted: str, attr: str = "router") -> None:
    try:
        module = __import__(dotted, fromlist=[attr])
        router = getattr(module, attr)
        dp.include_router(router)
        log.info("Router included: %s.%s", dotted, attr)
    except Exception as e:
        log.warning("Skip router %s: %s", dotted, e)


async def _set_bot_commands_everywhere(bot: Bot) -> None:
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


async def main() -> None:
    token = _resolve_token()
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()

    # init структур (если есть)
    await _init_db_if_available()

    # ⬇️ НОВОЕ: создаём пул и кладём в контекст бота
    await _create_db_pool_if_possible(bot)

    # Порядок: шорткаты → онбординг → доменные → системные → отзывы/премиум
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
    _include_router_safe(dp, "app.routers.analytics")  # отчёты по источникам
    _include_router_safe(dp, "app.routers.cancel")
    _include_router_safe(dp, "app.routers.feedback")
    _include_router_safe(dp, "app.routers.premium")  # <-- наш новый роутер

    await _set_bot_commands_everywhere(bot)

    log.info("Bot is starting polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Bot stopped")
