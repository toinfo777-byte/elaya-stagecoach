from __future__ import annotations

import asyncio
import importlib
import logging
import hashlib
from collections import Counter

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from app.config import settings
from app.storage.repo import ensure_schema

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
log = logging.getLogger("main")

# Маркер сборки — видно в логах
BUILD_MARK = "deploy-fixed-409-no-trace-dupfix-2025-10-06"

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
# Команды
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
# Вспомогалки
# ───────────────────────────────────────────────
def _include_router(dp: Dispatcher, router_obj, name: str):
    try:
        dp.include_router(router_obj)
        log.info("✅ router loaded: %s", name)
    except Exception:
        log.exception("❌ router failed: %s", name)

def _check_duplicate_handlers(dp: Dispatcher) -> None:
    """
    Диагностика дублей хэндлеров в подключенных роутерах (aiogram v3).
    Проходим по всем observers и их .handlers.
    """
    try:
        all_items: list[tuple[str, str, str]] = []  # (router_name, event_type, callback_qualname)

        # сам dp тоже роутер, но нам интересны подключённые
        for router in dp.sub_routers:
            rname = getattr(router, "name", "unknown")
            # router.observers: dict[str, TelegramEventObserver]
            for event_type, observer in router.observers.items():
                # observer.handlers: list[HandlerObject]
                for h in getattr(observer, "handlers", []):
                    cb = h.callback
                    cb_name = f"{getattr(cb, '__module__', '?')}.{getattr(cb, '__qualname__', getattr(cb, '__name__', '<?>'))}"
                    all_items.append((rname, event_type, cb_name))

        # считаем дубли по (event_type, callback_qualname)
        keys = [f"{ev}|{cb}" for _, ev, cb in all_items]
        counts = Counter(keys)
        dups = {k: c for k, c in counts.items() if c > 1}

        if not dups:
            log.info("✅ No duplicate handlers detected")
            return

        log.warning("⚠️ DUPLICATE HANDLERS DETECTED (%d):", len(dups))
        for key, cnt in dups.items():
            ev, cb = key.split("|", 1)
            places = [r for r, ev2, cb2 in all_items if ev2 == ev and cb2 == cb]
            log.warning("  %s  (%s)  ×%d  in %s", cb, ev, cnt, places)
    except Exception:
        log.exception("duplicate handlers check failed")

# ───────────────────────────────────────────────
# main
# ───────────────────────────────────────────────
async def main() -> None:
    log.info("=== BUILD %s ===", BUILD_MARK)

    # 1) Схема БД
    await ensure_schema()

    # 2) bot / dispatcher
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # 3) Сбрасываем возможный вебхук и «хвосты»
    await bot.delete_webhook(drop_pending_updates=True)
    log.info("Webhook deleted, pending updates dropped")

    # 4) entrypoints берём надёжно
    ep = importlib.import_module("app.routers.entrypoints")
    go_router = getattr(ep, "go_router", getattr(ep, "router"))
    log.info("entrypoints loaded: using %s", "go_router" if hasattr(ep, "go_router") else "router")

    # 5) Подключаем роутеры (важен порядок)
    _include_router(dp, go_router,            "entrypoints")
    _include_router(dp, help_router,          "help")
    _include_router(dp, cmd_aliases_router,   "cmd_aliases")

    _include_router(dp, mc_router,            "minicasting")
    _include_router(dp, leader_router,        "leader")
    _include_router(dp, tr_router,            "training")

    _include_router(dp, r_progress.router,    "progress")
    _include_router(dp, r_privacy.router,     "privacy")
    _include_router(dp, r_settings.router,    "settings")
    _include_router(dp, r_extended.router,    "extended")
    _include_router(dp, r_casting.router,     "casting")
    _include_router(dp, r_apply.router,       "apply")

    _include_router(dp, faq_router,           "faq")

    # 6) Команды
    await _set_commands(bot)
    log.info("✅ Команды установлены")

    # 7) Диагностика дублей
    _check_duplicate_handlers(dp)

    # 8) Хэш токена (для визуальной проверки, что крутится нужная конфигурация)
    token_hash = hashlib.md5(settings.bot_token.encode()).hexdigest()[:8]
    log.info("🔑 Token hash: %s", token_hash)

    # 9) Информация о боте (ещё одна проверка токена)
    me = await bot.get_me()
    log.info("🤖 Bot: @%s (ID: %s)", me.username, me.id)

    # 10) Polling
    log.info("🚀 Start polling…")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("⏹ Stopped by user")
