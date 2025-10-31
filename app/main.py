from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any, Iterable

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatType
from aiogram.types import Update, Message
from aiogram.filters import CommandStart

# === Глобальные метки билда/окружения ===
START_TS = time.time()
ENV = os.getenv("ENV", "staging")
MODE = os.getenv("MODE", "worker")
BUILD_MARK = os.getenv("BUILD_MARK", "manual")
ALLOW_GROUP_COMMANDS = set(
    cmd.strip() for cmd in os.getenv("ALLOW_GROUP_COMMANDS", "/hq,/healthz").split(",") if cmd.strip()
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("elaya.hq.main")

# === HQ-роутер ===
from app.routers.hq import hq_router  # noqa: E402


# =========================
# Middleware: ограничение команд в группах
# =========================
class GroupCommandGate:
    """
    Блокирует ВСЕ сообщения в группах, кроме разрешённых команд из ALLOW_GROUP_COMMANDS.
    Работает только для group/supergroup. В личке — не мешает.
    """

    def __init__(self, allow: Iterable[str]):
        self.allow = set(allow)

    async def __call__(self, handler, event: Update, data: dict[str, Any]):
        msg: Message | None = event.message or event.edited_message  # type: ignore
        if not msg:
            return await handler(event, data)

        if msg.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
            text = (msg.text or msg.caption or "").strip()
            if text.startswith("/"):
                # /cmd@BotUserName -> /cmd
                base = text.split()[0]
                base = base.split("@")[0]
                if base not in self.allow:
                    # Молча игнорируем
                    return
        return await handler(event, data)


# =========================
# Минимальный системный роутер (опционально)
# =========================
from aiogram import Router
sys_router = Router(name="sys")

@sys_router.message(CommandStart())
async def cmd_start(m: Message):
    await m.answer("Я HQ-бот Элайи. Доступные команды: /hq, /status_all, /healthz, /pong")


# =========================
# Инициализация и запуск
# =========================
async def run_bot() -> None:
    bot_token = os.getenv("TG_BOT_TOKEN")
    if not bot_token:
        raise RuntimeError("TG_BOT_TOKEN is empty")

    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Удаляем webhook (если когда-то был), и чистим «хвосты»,
    # чтобы не ловить TelegramConflictError при polling.
    await bot.delete_webhook(drop_pending_updates=True)

    # Подключаем middleware-фильтр для групп (можно оставить пустым ALLOW_GROUP_COMMANDS — тогда блокировки не будет)
    if ALLOW_GROUP_COMMANDS:
        dp.update.middleware(GroupCommandGate(ALLOW_GROUP_COMMANDS))

    # Подключаем роутеры
    dp.include_router(sys_router)
    dp.include_router(hq_router)

    log.info("Starting polling… ENV=%s MODE=%s BUILD=%s", ENV, MODE, BUILD_MARK)

    # Разрешаем только реально используемые типы апдейтов
    allowed_updates = dp.resolve_used_update_types()

    await dp.start_polling(
        bot,
        allowed_updates=allowed_updates,
    )


def main() -> None:
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
