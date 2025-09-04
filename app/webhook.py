# app/webhook.py
from __future__ import annotations
import os, logging, asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from app.config import settings
from app.storage.repo import init_db
from app.middlewares.error_handler import ErrorsMiddleware

# ваши роутеры
from app.routers import onboarding, menu
import app.routers.training as training
import app.routers.casting as casting
import app.routers.progress as progress

logging.basicConfig(level=logging.INFO)

def build_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.middleware(ErrorsMiddleware())
    dp.callback_query.middleware(ErrorsMiddleware())

    # порядок как в main.py
    dp.include_router(onboarding.router)
    dp.include_router(training.router)
    dp.include_router(casting.router)
    dp.include_router(progress.router)
    dp.include_router(menu.router)
    return dp

async def on_startup(app: web.Application):
    init_db()
    bot: Bot = app["bot"]
    base = os.getenv("RENDER_EXTERNAL_URL", "").rstrip("/")
    path = f"/webhook/{settings.bot_token}"
    if base:
        url = base + path
        await bot.set_webhook(url)
        logging.info("Webhook set to %s", url)
    else:
        logging.warning("RENDER_EXTERNAL_URL missing; webhook not set")

async def on_shutdown(app: web.Application):
    bot: Bot = app["bot"]
    await bot.delete_webhook(drop_pending_updates=False)

async def create_app() -> web.Application:
    bot = Bot(settings.bot_token)
    dp = build_dispatcher()

    app = web.Application()
    app["bot"] = bot
    app["dp"] = dp

    # healthcheck для Render
    async def health(_):
        return web.Response(text="OK")
    app.router.add_get("/", health)

    # регистрируем обработчик webhook
    SimpleRequestHandler(dp, bot).register(app, path=f"/webhook/{settings.bot_token}")
    setup_application(app, dp, bot=bot)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app

def main():
    app = asyncio.get_event_loop().run_until_complete(create_app())
    port = int(os.getenv("PORT", "8000"))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
