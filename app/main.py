from __future__ import annotations
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app.storage.repo import ensure_schema
from app.build import BUILD_MARK

# ======== OBSERVABILITY / SENTRY =========
from app.observability.sentry import init_sentry, capture_test_message

RELEASE = os.getenv("SHORT_SHA") or "local"
print("=== INIT SENTRY BLOCK EXECUTION ===")
init_sentry(
    dsn=os.getenv("SENTRY_DSN"),
    env=os.getenv("ENV", "prod"),
    release=RELEASE,
)
if os.getenv("ENV", "prod") != "prod":
    capture_test_message()
# ========================================


async def main() -> None:
    logging.basicConfig(level=settings.log_level)
    await ensure_schema()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # ===== ROUTERS =====
    from app.routers import (
        entrypoints,
        help,
        onboarding,
        system,
        minicasting,
        leader,
        training,
        progress,
        privacy,
        settings as settings_router,
        extended,
        casting,
        apply,
        faq,
        devops_sync,
        diag,
        panic,
    )

    # Подключаем безопасно aliases (если его нет — просто пропускаем)
    try:
        import app.routers.aliases as aliases
        dp.include_router(aliases.router)
        logging.info("✅ router loaded: aliases")
    except Exception as e:
        logging.warning(f"⚠️ router 'aliases' is missing or invalid: {e}")

    dp.include_router(entrypoints.router)
    dp.include_router(help.router)
    dp.include_router(onboarding.router)
    dp.include_router(system.router)
    dp.include_router(minicasting.router)
    dp.include_router(leader.router)
    dp.include_router(training.router)
    dp.include_router(progress.router)
    dp.include_router(privacy.router)
    dp.include_router(settings_router.router)
    dp.include_router(extended.router)
    dp.include_router(casting.router)
    dp.include_router(apply.router)
    dp.include_router(faq.router)
    dp.include_router(devops_sync.router)
    dp.include_router(panic.router)
    dp.include_router(diag.router)
    # ====================

    logging.info(f"=== BUILD {BUILD_MARK} ===")
    logging.info("🚀 Start polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
