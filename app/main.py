from __future__ import annotations
import asyncio, importlib, logging, hashlib
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from app.config import settings
from app.storage.repo import ensure_schema

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("main")

BUILD_MARK = "allowed-updates-callback-fix-2025-10-08"

# --- routers ---
# Главная навигация (рисует меню на 8 инлайн-кнопок и ловит go:*)
ep = importlib.import_module("app.routers.entrypoints")
go_router = getattr(ep, "go_router", getattr(ep, "router"))

# Страхующий системный роутер (логирует все callback'и и тоже умеет меню)
from app.routers.system import router as system_router

# Остальные разделы (оставляем как есть)
try:
    from app.routers.minicasting import mc_router
except Exception:
    from app.routers.minicasting import router as mc_router
from app.routers.training import router as tr_router
from app.routers.leader import router as leader_router
from app.routers.cmd_aliases import router as cmd_aliases_router
from app.routers import privacy as r_privacy, progress as r_progress, settings as r_settings, \
    extended as r_extended, casting as r_casting, apply as r_apply
from app.routers.onboarding import router as onboarding_router
from app.routers.faq import router as faq_router

async def _set_commands(bot: Bot) -> None:
    await bot.set_my_commands([
        BotCommand(command="start",    description="Запуск / меню"),
        BotCommand(command="menu",     description="Главное меню"),
        BotCommand(command="help",     description="FAQ / помощь"),
        BotCommand(command="training", description="Тренировка дня"),
        BotCommand(command="casting",  description="Мини-кастинг"),
        BotCommand(command="leader",   description="Путь лидера"),
        BotCommand(command="apply",    description="Заявка лидера"),
        BotCommand(command="progress", description="Мой прогресс"),
        BotCommand(command="privacy",  description="Политика"),
        BotCommand(command="settings", description="Настройки"),
        BotCommand(command="cancel",   description="Сбросить форму"),
        BotCommand(command="ping",     description="Проверка связи"),
        BotCommand(command="fixmenu",  description="Починить меню"),
    ])

def _include(dp: Dispatcher, router_obj, name: str):
    try:
        dp.include_router(router_obj)
        log.info("✅ router loaded: %s", name)
    except Exception:
        log.exception("❌ router failed: %s", name)

async def main() -> None:
    log.info("=== BUILD %s ===", BUILD_MARK)
    await ensure_schema()

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Сбрасываем вебхук и очередь
    await bot.delete_webhook(drop_pending_updates=True)
    log.info("Webhook deleted, pending updates dropped")

    # Порядок важен: сначала системный (лог), затем entrypoints (меню/го), затем прочее
    _include(dp, system_router, "system")
    _include(dp, go_router, "entrypoints")
    _include(dp, cmd_aliases_router, "cmd_aliases")
    _include(dp, onboarding_router, "onboarding")
    _include(dp, mc_router, "minicasting")
    _include(dp, leader_router, "leader")
    _include(dp, tr_router, "training")
    _include(dp, r_progress.router, "progress")
    _include(dp, r_privacy.router, "privacy")
    _include(dp, r_settings.router, "settings")
    _include(dp, r_extended.router, "extended")
    _include(dp, r_casting.router, "casting")
    _include(dp, r_apply.router, "apply")
    _include(dp, faq_router, "faq")

    await _set_commands(bot)
    log.info("✅ Команды установлены")

    me = await bot.get_me()
    log.info("🔑 Token hash: %s", hashlib.md5(settings.bot_token.encode()).hexdigest()[:8])
    log.info("🤖 Bot: @%s (ID: %s)", me.username, me.id)

    log.info("🚀 Start polling…")

    # 🔧 КЛЮЧЕВОЕ: ЯВНО РАЗРЕШАЕМ callback_query (и message)
    allowed = ["message", "callback_query"]
    await dp.start_polling(bot, allowed_updates=allowed)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("⏹ Stopped by user")
