from fastapi import FastAPI, Request, HTTPException
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Update

from app.config import settings
from app.routers import router as main_router


# --- Aiogram: бот и диспетчер ---

bot = Bot(
    token=settings.TG_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML"),
)

dp = Dispatcher()
dp.include_router(main_router)  # главный агрегирующий роутер


# --- FastAPI: ASGI-приложение для Render/вебхука ---

app = FastAPI()


@app.on_event("startup")
async def on_startup() -> None:
    """
    Старт бота: выставляем вебхук.
    """
    if settings.BASE_URL and settings.WEBHOOK_SECRET:
        await bot.set_webhook(
            url=f"{settings.BASE_URL}/tg/webhook",
            secret_token=settings.WEBHOOK_SECRET,
            drop_pending_updates=False,
        )


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """
    Остановка: аккуратно закрываем сессию.
    """
    await bot.session.close()


@app.post("/tg/webhook")
async def tg_webhook(request: Request):
    """
    Точка приёма апдейтов от Telegram.
    """
    # проверяем секрет, если он задан
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if settings.WEBHOOK_SECRET and secret != settings.WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="invalid secret token")

    data = await request.json()
    update = Update.model_validate(data)

    await dp.feed_update(bot, update)
    return {"ok": True}
