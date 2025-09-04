from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

from app.config import settings
from app.storage.repo import session_scope
from app.storage.models import User
from app.services.leads import export_leads_csv

router = Router(name="admin")

def _is_admin(uid: int) -> bool:
    try:
        admin_ids = {int(x) for x in settings.admin_ids}
    except Exception:
        admin_ids = set()
    return uid in admin_ids

@router.message(Command("admin"))
async def admin_help(m: Message):
    if not _is_admin(m.from_user.id):
        return
    await m.answer(
        "Админ:\n"
        "/broadcast <текст> — рассылка всем\n"
        "/leads_csv — выгрузка лидов CSV"
    )

@router.message(Command("broadcast"))
async def broadcast(m: Message):
    if not _is_admin(m.from_user.id):
        return
    text = m.text.partition(" ")[2].strip()
    if not text:
        await m.answer("Нужно так: /broadcast Текст сообщения")
        return
    sent = 0
    failed = 0
    from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

    async with m.bot.session:
        with session_scope() as s:
            users = s.query(User).all()
            for u in users:
                try:
                    await m.bot.send_message(u.tg_id, text)
                    sent += 1
                except (TelegramForbiddenError, TelegramBadRequest):
                    failed += 1
    await m.answer(f"Рассылка завершена. Отправлено: {sent}, ошибок: {failed}")

@router.message(Command("leads_csv"))
async def leads_csv(m: Message):
    if not _is_admin(m.from_user.id):
        return
    path = "exports/leads.csv"
    with session_scope() as s:
        export_leads_csv(s, path)
    await m.answer_document(FSInputFile(path), caption="Лиды (CSV)")
