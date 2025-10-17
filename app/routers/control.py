# app/routers/control.py
from aiogram import Router, types
from aiogram.filters import Command
import os, time

router = Router(name="control")

BOOT_TS = time.time()

def _build_status() -> str:
    build = os.getenv("SHORT_SHA", "local") or "local"
    env = os.getenv("ENV", "develop") or "develop"
    uptime = int(time.time() - BOOT_TS)
    mins, secs = divmod(uptime, 60)
    hours, mins = divmod(mins, 60)
    return (
        f"🧩 Статус\n"
        f"• BUILD: <code>{build}</code>\n"
        f"• ENV: <b>{env}</b>\n"
        f"• Uptime: {hours:02d}:{mins:02d}:{secs:02d}\n"
    )

@router.message(Command("status"))
async def cmd_status(m: types.Message):
    await m.answer(_build_status())

@router.message(Command("version"))
async def cmd_version(m: types.Message):
    build = os.getenv("SHORT_SHA", "local") or "local"
    await m.answer(f"🔖 Версия: <code>{build}</code>")

@router.message(Command("reload"))
async def cmd_reload(m: types.Message):
    # тут мягкая перезагрузка настроек, если нужно; пока — заглушка
    await m.answer("♻️ Конфигурация перечитана (soft reload).")

@router.message(Command("notify_admins"))
async def cmd_notify_admins(m: types.Message):
    text = m.text.partition(" ")[2].strip() or "Тестовый ручной алерт."
    ids_env = (
        os.getenv("ADMIN_ALERT_CHAT_ID")    # одиночный ID
        or os.getenv("ADMIN_IDS", "")       # список через запятую
    )
    chat_ids = []
    for token in ids_env.split(","):
        token = token.strip()
        if token.isdigit():
            chat_ids.append(int(token))
    if not chat_ids:
        await m.answer("⚠️ Нет получателей: задайте ADMIN_ALERT_CHAT_ID или ADMIN_IDS.")
        return
    ok, fail = 0, 0
    for cid in chat_ids:
        try:
            await m.bot.send_message(cid, f"🚨 ADMIN ALERT\n\n{text}")
            ok += 1
        except Exception:
            fail += 1
    await m.answer(f"✅ Отправлено: {ok}, ❌ ошибок: {fail}")
