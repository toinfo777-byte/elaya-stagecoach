# routers/premium.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.utils.formatting import Bold, Text, as_marked_section
import os
from datetime import datetime, timedelta, timezone

premium_router = Router()

ADMIN_ALERT_CHAT_ID = int(os.getenv("ADMIN_ALERT_CHAT_ID", "0"))

# --- вспомогалки ---

def user_link(m: Message) -> str:
    u = m.from_user
    # кликабельная ссылка, если есть username; иначе просто id
    if u.username:
        return f"@{u.username} (id={u.id})"
    return f"id={u.id}"

async def notify_admins(bot, text: str) -> None:
    if ADMIN_ALERT_CHAT_ID:
        try:
            await bot.send_message(ADMIN_ALERT_CHAT_ID, text, disable_web_page_preview=True)
        except Exception as e:
            # не падаем, просто логни где-то у себя
            print(f"[premium] admin notify failed: {e}")

async def already_sent_recently(pool, user_id: int, hours: int = 24) -> bool:
    """Есть ли заявка за последние `hours` часов."""
    async with pool.acquire() as con:
        row = await con.fetchrow(
            """
            SELECT 1
            FROM pro_requests
            WHERE user_id = $1
              AND ts > now() - $2::interval
            LIMIT 1
            """,
            user_id, f"{hours} hours"
        )
    return row is not None

async def save_request(pool, m: Message, note: str | None) -> None:
    async with pool.acquire() as con:
        await con.execute(
            """
            INSERT INTO pro_requests(user_id, username, note)
            VALUES ($1, $2, $3)
            """,
            m.from_user.id, m.from_user.username, note
        )

# --- хэндлеры ---

# Кнопка из меню
@premium_router.message(F.text == "⭐️ Расширенная версия")
async def premium_button(message: Message):
    await handle_pro_request(message, note="from:menu_button")

# Команда /pro (на всякий)
@premium_router.message(F.text.startswith("/pro"))
async def premium_cmd(message: Message):
    # можно позволить писать комментарий: /pro хочу личные разборы
    note = message.text.partition(" ")[2].strip() or None
    await handle_pro_request(message, note=note)

# Общая логика
async def handle_pro_request(message: Message, note: str | None):
    bot = message.bot
    pool = bot.get("db_pool")  # <- см. подключение ниже

    # антиспам на 24 часа
    if await already_sent_recently(pool, message.from_user.id, hours=24):
        await message.answer("✅ Заявка уже есть, мы свяжемся. Спасибо!")
        return

    await save_request(pool, message, note)

    await message.answer(
        "✅ Заявка на ⭐️ Расширенную версию принята!\n"
        "Мы напишем вам в личку, как только будет свободное окно."
    )

    # уведомление админам
    when = datetime.now(timezone.utc).astimezone().strftime("%d.%m %H:%M")
    text = as_marked_section(
        Bold("⭐️ Новая заявка на PRO"),
        Text(
            f"Пользователь: {user_link(message)}",
            f"Когда: {when}",
            f"Источник: {note or '—'}",
            sep="\n",
        )
    ).as_html()
    await notify_admins(bot, text)

# (опционально) мини-статистика за 7 дней для админов: /pro_stats
@premium_router.message(F.text == "/pro_stats")
async def pro_stats(message: Message):
    # доступ только админам — если у тебя есть список ADMIN_IDS, проверь тут
    admin_ids = {int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()}
    if admin_ids and message.from_user.id not in admin_ids:
        return

    pool = message.bot.get("db_pool")
    async with pool.acquire() as con:
        row = await con.fetchrow(
            "SELECT COUNT(*) AS c FROM pro_requests WHERE ts > now() - interval '7 days'"
        )
        c7 = row["c"] if row else 0
        row = await con.fetchrow(
            "SELECT COUNT(*) AS c FROM pro_requests WHERE ts > now() - interval '24 hours'"
        )
        c1 = row["c"] if row else 0

    await message.answer(f"⭐️ PRO заявки: за 24ч — {c1}, за 7д — {c7}")
