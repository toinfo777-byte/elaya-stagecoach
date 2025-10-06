from __future__ import annotations

import asyncio
import importlib
import logging
import hashlib
from collections import Counter

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from app.config import settings
from app.storage.repo import ensure_schema

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
log = logging.getLogger("main")

BUILD_MARK = "deploy-fixed-no-trace-2025-10-06"

# ── роутеры ───────────────────────────────────────────────────────────────────
from app.routers.faq import router as faq_router
from app.routers.training import router as tr_router
from app.routers.leader import router as leader_router
from app.routers.cmd_aliases import router as cmd_aliases_router
try:
    from app.routers.minicasting import mc_router
except Exception:
    from app.routers.minicasting import router as mc_router
from app.routers import (
    privacy as r_privacy,
    progress as r_progress,
    settings as r_settings,
    extended as r_extended,
    casting as r_casting,
    apply as r_apply,
)
# ──────────────────────────────────────────────────────────────────────────────

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

def _include_router(dp: Dispatcher, router_obj, name: str):
    try:
        dp.include_router(router_obj)
        log.info("✅ router loaded: %s", name)
    except Exception:
        log.exception("❌ router failed: %s", name)

def _check_duplicate_handlers(dp: Dispatcher):
    all_handlers = []
    for router in dp.sub_routers:
        rname = getattr(router, "name", "unknown")
        for event_type, observers in router.observers.items():
            for handler in observers:
                all_handlers.append((rname, handler.callback.__name__, event_type))
    names = [h[1] for h in all_handlers]
    dup = {n: names.count(n) for n in set(names) if names.count(n) > 1}
    if dup:
        log.warning("⚠️ Duplicate handlers: %s", dup)
    else:
        log.info("✅ No duplicate handlers detected")

def _make_session() -> AiohttpSession:
    # ВАЖНО: без trace_configs — иначе падает на вашей версии aiogram
    return AiohttpSession()

async def main() -> None:
    log.info("=== BUILD %s ===", BUILD_MARK)

    # 1) схема БД
    await ensure_schema()

    # 2) bot / dispatcher + session
    session = _make_session()
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session,
    )
    dp = Dispatcher()

    # 3) сброс вебхука/апдейтов
    await bot.delete_webhook(drop_pending_updates=True)
    log.info("Webhook deleted, pending updates dropped")

    # 4) входные точки
    ep = importlib.import_module("app.routers.entrypoints")
    go_router = getattr(ep, "go_router", getattr(ep, "router"))
    log.info("entrypoints loaded: using %s", "go_router" if hasattr(ep, "go_router") else "router")

    # 5) порядок роутеров
    _include_router(dp, go_router, "entrypoints")
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

    # 7) диагностика
    _check_duplicate_handlers(dp)
    token_hash = hashlib.md5(settings.bot_token.encode()).hexdigest()[:8]
    log.info("🔑 Token hash: %s", token_hash)
    me = await bot.get_me()
    log.info("🤖 Bot: @%s (ID: %s)", me.username, me.id)

    # 8) polling
    log.info("🚀 Start polling…")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("⏹ Stopped by user")
