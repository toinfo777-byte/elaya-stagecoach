import asyncio
import logging
import importlib
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.middlewares.error_handler import ErrorsMiddleware
from app.storage.repo import init_db

# Базовые роутеры (точно есть)
from app.routers import onboarding
import app.routers.training as training
import app.routers.casting as casting
import app.routers.progress as progress
from app.routers import menu

# ⬇️ НОВОЕ: системный роутер (/help, /privacy и техкоманды)
from app.routers import system  # NEW

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

def _include_optional_router(dp: Dispatcher, module_path: str, attr: str = "router") -> Optional[None]:
    """
    Пытаемся подключить роутер из module_path.attr.
    Если ничего нет — просто логируем и идём дальше.
    """
    try:
        mod = importlib.import_module(module_path)
        r = getattr(mod, attr)
    except Exception as e:
        logging.info("Skip router %s (%s)", module_path, e)
        return None
    dp.include_router(r)
    logging.info("Included router: %s.%s", module_path, attr)
    return None

async def main():
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is empty. Set it in .env")

    # Инициализируем БД/таблицы
    init_db()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    # Глобальная обработка ошибок
    dp.message.middleware(ErrorsMiddleware())
    dp.callback_query.middleware(ErrorsMiddleware())

    # 1) Специализированные/служебные роутеры (если имеются в проекте)
    _include_optional_router(dp, "app.routers.help")       # help_router.router
    _include_optional_router(dp, "app.routers.settings")   # settings_router.router
    _include_optional_router(dp, "app.routers.admin")      # admin.router (последний из служебных)
    _include_optional_router(dp, "app.routers.premium")    # premium.router

    # ⬇️ НОВОЕ: подключаем наш системный роутер
    dp.include_router(system.router)  # NEW

    # 2) Ваши основные фичи
    dp.include_router(onboarding.router)
    dp.include_router(training.router)
    dp.include_router(casting.router)
    dp.include_router(progress.router)

    # 3) Меню — строго последним
    dp.includ
