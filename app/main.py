from __future__ import annotations
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app.storage.repo import ensure_schema
from app.build import BUILD_MARK

# Routers
from app.routers import (
    entrypoints,
    help,
    aliases,
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
    panic,  # новый роутер
)

# ======== SENTRY INTEGRATION =========
try:
    if settings.sentry_dsn:
        import sentry_sdk
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            enable_tracing=False,
            traces_sample_rate=0.0,
            profiles_sample_rate=0.0,
            send_default_pii=False,
        )
        print("SENTRY: initialized ✅")
    else:
        print("SENTRY: DSN not provided ⚠️")
except Exception as e:
    print(f"SENTRY: init failed ❌ {e}")
# ====================================


async def main() -> None:
    logging.basicConfig(level=settings.log_level)
    await ensure_schema()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()

    # Register routers
    dp.include_router(entrypoints.router)
    dp.include_router(help.router)
    dp.include_router(aliases.router)
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
    dp.include_router(panic.router)  # добавляем паник
    dp.include_router(diag.router)

    logging.info(f"=== BUILD {BUILD_MARK} ===")
    logging.info("🚀 Start polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
