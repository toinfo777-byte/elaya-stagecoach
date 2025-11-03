# app/main.py
from __future__ import annotations

import os
import asyncio
import logging
import random
from typing import Optional

from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramConflictError

from app.config import settings
from app.build import BUILD_MARK

dp: Optional[Dispatcher] = None
bot: Optional[Bot] = None

# --- Логи ---
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("elaya.main")

# --- FastAPI (используется только когда MODE=web) ---
app = FastAPI(title="Elaya StageCoach", version=BUILD_MARK)


@app.get("/healthz")
async def healthz():
    """Простой healthcheck для Render."""
    loop = asyncio.get_event_loop()
    return {"ok": True, "uptime_s": int(loop.time())}


# ---------- Роутеры по профилю ----------
def _include_routers_for_profile(dp: Dispatcher, profile: str) -> None:
    """
    Подключаем только необходимые роутеры по роли сервиса.
    profile:
      - "hq"       -> минимальный набор для HQ worker
      - "trainer"  -> пользовательские разделы тренера
      - "web"      -> ничего не добавляем (FastAPI обслужит /healthz)
      - любое другое -> как "hq"
    """
    # базовые HQ-роутеры (системные + штаб)
    from app.routers import system, hq

    # временный дебаг-роутер (можно убрать после проверки)
    try:
        from app.routers import debug
        dp.include_router(debug.router)
    except Exception as e:
        logger.warning("debug router not loaded: %s", e)

    dp.include_router(system.router)
    dp.include_router(hq.router)

    profile = (profile or "hq").lower()
    if profile == "trainer":
        # Полный набор пользовательских разделов
        from app.routers import (
            help as help_router,
            cmd_aliases,
            onboarding,
            minicasting,
            leader,
            training,
            progress,
            privacy,
            settings as settings_mod,
            extended,
            casting,
            apply,
            faq,
            devops_sync,
            panic,
        )
        dp.include_router(help_router.router)
        dp.include_router(cmd_aliases.router)
        dp.include_router(onboarding.router)
        dp.include_router(minicasting.router)
        dp.include_router(leader.router)
        dp.include_router(training.router)
        dp.include_router(progress.router)
        dp.include_router(privacy.router)
        dp.include_router(settings_mod.router)
        dp.include_router(extended.router)
        dp.include_router(casting.router)
        dp.include_router(apply.router)
        dp.include_router(faq.router)
        dp.include_router(devops_sync.router)
        dp.include_router(panic.router)
    elif profile == "web":
        # для чистого веб-профиля роутеры бота не подключаем
        pass
    else:
        # "hq" / неизвестный -> остаёмся на системном минимуме
        pass


# ---------- Telegram Bot worker ----------
async def start_polling() -> None:
    """
    Конфликто-устойчивый запуск polling:
    - опциональная пауза STARTUP_DELAY перед стартом (даём старому инстансу умереть)
    - управляемый ретрай по TelegramConflictError до CONFLICT_TIMEOUT
    """
    global dp, bot

    # 0) Опциональная стартовая задержка для избежания гонки инстансов Render
    startup_delay = int(os.getenv("STARTUP_DELAY", "0"))
    if startup_delay > 0:
        logger.info("Startup delay: %s sec (to avoid overlap)", startup_delay)
        await asyncio.sleep(startup_delay)

    bot = Bot(
        token=settings.TG_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # сколько времени терпим конфликты (сек)
    max_conflict_seconds = int(os.getenv("CONFLICT_TIMEOUT", "120"))
    started_at = asyncio.get_event_loop().time()

    try:
        # 1) Снимаем вебхук (иначе getUpdates конфликтует с webhook)
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info("Webhook deleted (drop_pending_updates=True).")
        except TelegramBadRequest as e:
            logger.warning("delete_webhook: %s (ignored)", e)

        # 2) Dispatcher + профиль роутеров
        dp = Dispatcher()
        profile = os.getenv("BOT_PROFILE", "hq")
        logger.info("Launching with BOT_PROFILE=%s", profile)
        _include_routers_for_profile(dp, profile)

        logger.info(
            "bot routers loaded; ENV=%s MODE=%s BUILD=%s",
            settings.ENV, settings.MODE, BUILD_MARK,
        )

        # 3) Разрешаем только реально используемые типы апдейтов
        used = dp.resolve_used_update_types()
        logger.info("allowed_updates=%s", used)

        # 4) Конфликто-устойчивый запуск polling с бэкоффом
        attempt = 0
        while True:
            try:
                await dp.start_polling(bot, allowed_updates=used)
                break  # если вышли отсюда — polling завершился штатно
            except TelegramConflictError as e:
                elapsed = asyncio.get_event_loop().time() - started_at
                attempt += 1
                if elapsed >= max_conflict_seconds:
                    logger.error("Conflict persists > %ss, giving up. %s", max_conflict_seconds, e)
                    # Завершаем процесс — Render перезапустит позже, когда старый инстанс умрет
                    raise
                backoff = min(5.0 + attempt * 0.5, 10.0) + random.uniform(0, 1.5)
                logger.warning(
                    "Conflict (attempt=%s, elapsed=%.1fs). Sleep %.2fs and retry...",
                    attempt, elapsed, backoff
                )
                await asyncio.sleep(backoff)

    finally:
        if dp:
            await dp.storage.close()
        if bot:
            await bot.session.close()


# ---------- Главная точка входа ----------
def run_app():
    """
    MODE=web    -> запускаем только FastAPI
    MODE=worker -> запускаем Telegram polling
    """
    mode = settings.MODE.lower()
    if mode == "web":
        logger.info("Starting WEB app... ENV=%s MODE=web BUILD=%s", settings.ENV, BUILD_MARK)
        return app
    elif mode == "worker":
        logger.info("Starting BOT polling... ENV=%s MODE=worker BUILD=%s", settings.ENV, BUILD_MARK)
        asyncio.run(start_polling())
    else:
        raise RuntimeError(f"Unknown MODE={settings.MODE!r}")


if __name__ == "__main__":
    run_app()
