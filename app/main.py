from __future__ import annotations

import asyncio
import importlib
import logging
import hashlib
import os
from collections import Counter
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from app.config import settings
from app.storage.repo import ensure_schema

# Логи
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
log = logging.getLogger("main")

BUILD_MARK = "deploy-fixed-409-trace-2025-10-01"

# ───────────────────────────────────────────────
# Роутеры
# ───────────────────────────────────────────────
from app.routers.faq import router as faq_router
from app.routers.help import help_router

try:
    from app.routers.minicasting import mc_router
except Exception:
    from app.routers.minicasting import router as mc_router

from app.routers.training import router as tr_router
from app.routers.leader import router as leader_router
from app.routers.cmd_aliases import router as cmd_aliases_router

from app.routers import (
    privacy as r_privacy,
    progress as r_progress,
    settings as r_settings,
    extended as r_extended,
    casting as r_casting,
    apply as r_apply,
)

# ───────────────────────────────────────────────
# Команды бота
# ───────────────────────────────────────────────
async def _set_commands(bot: Bot) -> None:
    cmds = [
        BotCommand(command="start", description="Запуск / онбординг"),
        BotCommand(command="menu", description="Главное меню"),
        BotCommand(command="training", description="Тренировка дня"),
        BotCommand(command="casting", description="Мини-кастинг"),
        BotCommand(command="progress", description="Мой прогресс"),
        BotCommand(command="apply", description="Путь лидера"),
        BotCommand(command="privacy", description="Политика"),
        BotCommand(command="extended", description="Расширенная версия"),
        BotCommand(command="help", description="FAQ / помощь"),
        BotCommand(command="settings", description="Настройки"),
        BotCommand(command="cancel", description="Сбросить форму"),
    ]
    await bot.set_my_commands(cmds)

# ───────────────────────────────────────────────
# Подключение роутеров с логом
# ───────────────────────────────────────────────
def _include_router(dp: Dispatcher, router_obj, name: str):
    try:
        dp.include_router(router_obj)
        log.info("✅ router loaded: %s", name)
    except Exception:
        log.exception("❌ router failed: %s", name)

# ───────────────────────────────────────────────
# Диагностика дублей хендлеров
# ───────────────────────────────────────────────
def _check_duplicate_handlers(dp: Dispatcher):
    """Проверка дублей по имени callback-функции (индикатор случайных двойных хендлеров)."""

    def collect(router) -> list[tuple[str, str, Any]]:
        items = []
        router_name = getattr(router, 'name', 'dispatcher')
        for event_type, observers in router.observers.items():
            for handler in observers:
                cb = getattr(handler, "callback", None)
                name = getattr(cb, "__name__", str(cb))
                items.append((router_name, name, event_type))
        for sub in router.sub_routers:
            items.extend(collect(sub))
        return items

    all_handlers = collect(dp)
    names = [h[1] for h in all_handlers]
    counts = Counter(names)
    dups = {n: c for n, c in counts.items() if c > 1}

    if dups:
        log.warning("⚠️ DUPLICATE HANDLERS DETECTED:")
        for name, cnt in dups.items():
            locations = [(r, e) for r, n, e in all_handlers if n == name]
            log.warning("  %s: %d times in %s", name, cnt, locations)
    else:
        log.info("✅ No duplicate handlers detected")

# ───────────────────────────────────────────────
# HTTP-трейс Telegram (диагностика)
# ───────────────────────────────────────────────
def _make_session() -> AiohttpSession:
    """Создаёт AiohttpSession с опциональным трейсингом HTTP (включается TELEGRAM_HTTP_DEBUG=1)."""
    debug = os.getenv("TELEGRAM_HTTP_DEBUG", "0") == "1"
    if not debug:
        return AiohttpSession()

    import aiohttp

    async def on_request_start(session, ctx, params):
        try:
            # Логируем только Telegram API вызовы
            url = str(params.url)
            if "api.telegram.org" in url:
                log.info("↗️  HTTP START %s %s", params.method, url)
        except Exception:
            pass

    async def on_request_end(session, ctx, params):
        try:
            url = str(params.url)
            if "api.telegram.org" in url:
                status = getattr(getattr(ctx, "response", None), "status", None)
                log.info("↘️  HTTP END   %s %s  status=%s", params.method, url, status)
        except Exception:
            pass

    async def on_request_exception(session, ctx, params):
        try:
            url = str(params.url)
            if "api.telegram.org" in url:
                log.warning("💥 HTTP EXC    %s %s  exc=%s", params.method, url, getattr(ctx, "exception", None))
        except Exception:
            pass

    trace = aiohttp.TraceConfig()
    trace.on_request_start.append(on_request_start)
    trace.on_request_end.append(on_request_end)
    trace.on_request_exception.append(on_request_exception)

    return AiohttpSession(trace_configs=[trace])

# ───────────────────────────────────────────────
# main()
# ───────────────────────────────────────────────
async def main() -> None:
    log.info("=== BUILD %s ===", BUILD_MARK)

    # 1) схема БД
    await ensure_schema()

    # 2) bot / dispatcher (+ сессия с трейсом, если включён)
    session = _make_session()
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session,
    )
    dp = Dispatcher()

    # 3) сброс webhook / висячих апдейтов
    await bot.delete_webhook(drop_pending_updates=True)
    log.info("Webhook deleted, pending updates dropped")

    # 4) входной роутер (entrypoints)
    ep = importlib.import_module("app.routers.entrypoints")
    go_router = getattr(ep, "go_router", getattr(ep, "router"))
    log.info("entrypoints loaded: using %s", "go_router" if hasattr(ep, "go_router") else "router")

    # 5) порядок роутеров
    _include_router(dp, go_router, "entrypoints")
    _include_router(dp, help_router, "help")
    _include_router(dp, cmd_aliases_router, "cmd_aliases")
    _include_router(dp, mc_router, "minicasting")
    _include_router(dp, leader_router, "leader")
    _include_router(dp, tr_router, "training")
    _include_router(dp, r_progress.router, "progress")
    _include_router(dp, r_privacy.router, "privacy")
    _include_router(dp, r_settings.router, "settings")
    _include_router(dp, r_extended.router, "extended")
    _include_router(dp, r_casting.router, "casting")
    _include_router(dp, r_apply.router, "apply")
    _include_router(dp, faq_router, "faq")

    # 6) команды
    await _set_commands(bot)
    log.info("✅ Команды установлены")

    # 7) диагностика дублей
    _check_duplicate_handlers(dp)

    # 8) диагностика токена/бота
    token_hash = hashlib.md5(settings.bot_token.encode()).hexdigest()[:8]
    log.info("🔑 Token hash: %s", token_hash)
    me = await bot.get_me()
    log.info("🤖 Bot: @%s (ID: %s)", me.username, me.id)

    # 9) polling (доп. ремень безопасности)
    log.info("🚀 Start polling…")
    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=True,
        )
    finally:
        # Чисто закрываем HTTP-сессию
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("⏹ Stopped by user")
