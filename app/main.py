from __future__ import annotations
import asyncio
import logging
import os
import importlib

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


def _parse_log_level(value) -> int:
    """
    Переводит любые варианты значения в корректный уровень для logging.
    Допускает: "INFO", "warning", 20, а также кривые строки вида "INFO / WARNING / DEBUG".
    """
    if isinstance(value, int):
        return value
    if value is None:
        return logging.INFO

    s = str(value).strip().upper()
    # если пришло "INFO / WARNING / DEBUG" или подобное — берём первый валидный токен
    for token in s.replace("/", " ").replace(",", " ").split():
        if token in logging._nameToLevel:
            return logging._nameToLevel[token]
    # если токены не подошли — пробуем целиком
    return logging._nameToLevel.get(s, logging.INFO)


def include_router_if_exists(dp: Dispatcher, module_name: str, exported_attr: str = "router") -> None:
    """Импортирует app.routers.<module_name> и включает dp.include_router(...), если модуль/атрибут есть."""
    full_name = f"app.routers.{module_name}"
    try:
        module = importlib.import_module(full_name)
    except Exception as e:
        logging.warning(f"⚠️ router module not found: {full_name} ({e})")
        return
    router = getattr(module, exported_attr, None)
    if router is None:
        logging.warning(f"⚠️ router attr '{exported_attr}' missing in {full_name}")
        return
    dp.include_router(router)
    logging.info(f"✅ router loaded: {module_name}")


async def main() -> None:
    # --- Логи: парсим уровень безопасно ---
    log_level = _parse_log_level(getattr(settings, "log_level", None))
    logging.basicConfig(level=log_level)
    logging.info(f"Logging level set to: {logging.getLevelName(log_level)}")

    await ensure_schema()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Подключаем роутеры (порядок сохранён). Любой отсутствующий — не валит процесс.
    for name in [
        "entrypoints",
        "help",
        "aliases",        # если нет файла/экспорта — будет предупреждение
        "onboarding",
        "system",
        "minicasting",
        "leader",
        "training",
        "progress",
        "privacy",
        "settings",
        "extended",
        "casting",
        "apply",
        "faq",
        "devops_sync",
        "panic",
        "diag",
    ]:
        include_router_if_exists(dp, name)

    logging.info(f"=== BUILD {BUILD_MARK} ===")
    logging.info("🚀 Start polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
