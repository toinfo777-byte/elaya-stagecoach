from __future__ import annotations

import asyncio
import importlib
import logging
import sys
import hashlib
from collections import Counter

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from app.config import settings
from app.storage.repo import ensure_schema

# Настроим логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
log = logging.getLogger("main")

# Маркер сборки — помогает понять, что крутится нужный образ
BUILD_MARK = "deploy-fixed-duplicates-2025-01-09"

# ───────────────────────────────────────────────
# Роутеры разделов
# ───────────────────────────────────────────────

# FAQ — отдельный роутер
from app.routers.faq import router as faq_router

# Help — главное меню и публичные функции
from app.routers.help import help_router

# Мини-кастинг: поддержим оба экспорта (mc_router или router)
try:
    from app.routers.minicasting import mc_router
except Exception:
    from app.routers.minicasting import router as mc_router

# Тренировка дня и Путь лидера
from app.routers.training import router as tr_router
from app.routers.leader import router as leader_router

# Прокси для слэш-команд (/training, /casting) с безопасным вызовом (obj, state)/(obj)
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
    try:
        dp.include_router(router_obj)
        log.info("✅ router loaded: %s", name)
    except Exception:
        log.exception("❌ router failed: %s", name)

# ───────────────────────────────────────────────
# Диагностика дублей хендлеров
# ───────────────────────────────────────────────
def _check_duplicate_handlers(dp: Dispatcher):
    """Проверка на дублирующиеся хендлеры"""
    all_handlers = []
    
    for router in dp.sub_routers:
        router_name = getattr(router, 'name', 'unknown')
        # Проверяем все типы обсерверов
        for event_type, observers in router.observers.items():
            for handler in observers:
                handler_name = handler.callback.__name__
                all_handlers.append((router_name, handler_name, event_type))
    
    # Ищем дубли по имени функции
    handler_names = [h[1] for h in all_handlers]
    counts = Counter(handler_names)
    duplicates = {name: count for name, count in counts.items() if count > 1}
    
    if duplicates:
        log.warning("⚠️ DUPLICATE HANDLERS DETECTED:")
        for name, count in duplicates.items():
            locations = [(r, e) for r, h, e in all_handlers if h == name]
            log.warning("  %s: %d times in %s", name, count, locations)
    else:
        log.info("✅ No duplicate handlers detected")

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
    await bot.delete_webhook(drop_pending_updates=True)
    log.info("Webhook deleted, pending updates dropped")

    # 4) входной роутер (entrypoints) тянем надёжно через importlib
    ep = importlib.import_module("app.routers.entrypoints")
    go_router = getattr(ep, "go_router", getattr(ep, "router"))
    log.info("entrypoints loaded: using %s", "go_router" if hasattr(ep, "go_router") else "router")

    # 5) порядок роутеров ВАЖЕН (первый = высший приоритет)
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

    # 8) диагностика токена
    token_hash = hashlib.md5(settings.bot_token.encode()).hexdigest()[:8]
    log.info("🔑 Token hash: %s", token_hash)

    # 9) информация о боте
    me = await bot.get_me()
    log.info("🤖 Bot: @%s (ID: %s)", me.username, me.id)

    # 10) polling
    log.info("🚀 Start polling…")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("⏹ Stopped by user")
