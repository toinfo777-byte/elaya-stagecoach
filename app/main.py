# app/main.py
from __future__ import annotations

import asyncio
import importlib
import logging
import hashlib

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from app.config import settings
from app.storage.repo import ensure_schema

# ──────────────────────────────────────────────────────────────────────────────
# Логирование
# ──────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("main")

# Маркер сборки
BUILD_MARK = "deploy-fixed-loggedout-2025-10-06"

# ───────────────────────────────────────────────
# Роутеры разделов
# ───────────────────────────────────────────────

# FAQ — отдельный роутер
from app.routers.faq import router as faq_router

# Help — короткое меню/помощь
try:
    from app.routers.help import help_router  # если есть
except Exception:
    help_router = None  # необязательно

# Мини-кастинг: поддержим оба экспорта (mc_router или router)
try:
    from app.routers.minicasting import mc_router
except Exception:
    from app.routers.minicasting import router as mc_router  # type: ignore

# Тренировка дня и Путь лидера
from app.routers.training import router as tr_router
from app.routers.leader import router as leader_router

# Прокси для слэш-команд (/training, /casting)
from app.routers.cmd_aliases import router as cmd_aliases_router

# Остальные модули (используем .router внутри)
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
# Утилита для подключения роутеров
# ───────────────────────────────────────────────
def _include_router(dp: Dispatcher, router_obj, name: str):
    if router_obj is None:
        return
    try:
        dp.include_router(router_obj)
        log.info("✅ router loaded: %s", name)
    except Exception:
        log.exception("❌ router failed: %s", name)

# ───────────────────────────────────────────────
# Точка входа
# ───────────────────────────────────────────────
async def main() -> None:
    log.info("=== BUILD %s ===", BUILD_MARK)

    # 1) схема БД
    await ensure_schema()

    # 2) bot / dispatcher
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # 3) сбрасываем webhook и висячие апдейты
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        log.info("Webhook deleted, pending updates dropped")
    except Exception as e:
        # Если до этого вызывали /logOut, Bot API отвечает "Logged out"
        if "Logged out" in str(e):
            log.warning("delete_webhook skipped: token is in 'Logged out' state")
        else:
            log.exception("delete_webhook failed")

    # 4) входной роутер (entrypoints) тянем надёжно через importlib
    ep = importlib.import_module("app.routers.entrypoints")
    go_router = getattr(ep, "go_router", getattr(ep, "router"))
    log.info(
        "entrypoints loaded: using %s",
        "go_router" if hasattr(ep, "go_router") else "router",
    )

    # 5) порядок роутеров ВАЖЕН (первый — с наибольшим приоритетом)
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

    # 7) полезные diagnost logs
    token_hash = hashlib.md5(settings.bot_token.encode()).hexdigest()[:8]
    log.info("🔑 Token hash: %s", token_hash)
    try:
        me = await bot.get_me()
        log.info("🤖 Bot: @%s (ID: %s)", me.username, me.id)
    except Exception:
        log.exception("get_me failed (проверь токен)")

    # 8) polling
    log.info("🚀 Start polling…")
    await dp.start_polling(
        bot,
        allowed_updates=dp.resolve_used_update_types(),
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("⏹ Stopped by user")
