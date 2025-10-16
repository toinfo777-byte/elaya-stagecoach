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

# === OBSERVABILITY / SENTRY (должно быть самым первым) =======================
from app.observability.sentry import init_sentry, capture_test_message

RELEASE = os.getenv("SHORT_SHA") or "local"          # выставляем из Render env
ENV = os.getenv("ENV", "prod")                       # develop / prod

print("=== INIT SENTRY BLOCK EXECUTION ===")
init_sentry(
    dsn=os.getenv("SENTRY_DSN"),
    env=ENV,
    release=RELEASE,
)
if ENV != "prod":
    capture_test_message()
# ============================================================================

async def main() -> None:
    # Приводим LOG_LEVEL к валидному значению (INFO/DEBUG/WARNING/ERROR)
    level = (os.getenv("LOG_LEVEL") or "INFO").strip().upper()
    level = {"INFO": "INFO", "DEBUG": "DEBUG", "WARNING": "WARNING", "ERROR": "ERROR"}.get(level, "INFO")
    logging.basicConfig(level=getattr(logging, level))
    logging.info(f"Logging level set to: {level}")

    await ensure_schema()
    logging.info("✅ Schema ensured")

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Routers (без падения, если какого-то нет)
    from importlib import import_module
    def safe_include(module_name: str, name: str):
        try:
            module = import_module(module_name)
            dp.include_router(getattr(module, "router"))
            logging.info(f"✅ router loaded: {name}")
        except Exception as e:
            logging.warning(f"⚠️ router module not found: {module_name} ({e})")

    safe_include("app.routers.entrypoints", "entrypoints")
    safe_include("app.routers.help", "help")
    safe_include("app.routers.aliases", "aliases")     # если нет — просто предупреждение
    safe_include("app.routers.onboarding", "onboarding")
    safe_include("app.routers.system", "system")
    safe_include("app.routers.minicasting", "minicasting")
    safe_include("app.routers.leader", "leader")
    safe_include("app.routers.training", "training")
    safe_include("app.routers.progress", "progress")
    safe_include("app.routers.privacy", "privacy")
    safe_include("app.routers.settings", "settings")
    safe_include("app.routers.extended", "extended")
    safe_include("app.routers.casting", "casting")
    safe_include("app.routers.apply", "apply")
    safe_include("app.routers.faq", "faq")
    safe_include("app.routers.devops_sync", "devops_sync")
    safe_include("app.routers.panic", "panic")
    safe_include("app.routers.diag", "diag")

    logging.info(f"=== BUILD {BUILD_MARK} ===")
    logging.info("🚀 Start polling…")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
