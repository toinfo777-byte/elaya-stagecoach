from __future__ import annotations

import csv
import os
import tempfile

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from app.config import settings
from app.storage.repo import session_scope
from app.storage.models import User, Lead

router = Router(name="admin")


# ---- helpers ----
def _admin_ids_set() -> set[int]:
    """Безопасно читаем settings.admin_ids (list|set|tuple|str '1,2,3')."""
    try:
        ids = settings.admin_ids
        if isinstance(ids, (set, list, tuple)):
            return {int(x) for x in ids}
        if isinstance(ids, str):
            parts = ids.replace(";", ",").split(",")
            return {int(x.strip()) for x in parts if x.strip()}
    except Exception:
        pass
    return set()


def _is_admin(uid: int) -> bool:
    return uid in _admin_ids_set()


# ---- commands ----
@router.message(Command("admin"))
async def admin_help(m: Message):
    if not _is_admin(m.from_user.id):
        return
    await m.answer(
        "Админ команды:\n"
        "/broadcast <текст> — рассылка всем пользователям\n"
        "/leads_csv — выгрузка лидов (CSV)"
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

    # читаем список юзеров одной сессией
    with session_scope() as s:
        users = s.query(User).all()

    # шлём сообщения
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
        return await m.answer("⛔ Только для админов.")

    # собираем данные Lead + User
    with session_scope() as s:
        q = (
            s.query(Lead, User)
            .join(User, User.id == Lead.user_id)
            .order_by(Lead.ts.desc())
        )
        rows = [
            {
                "ts": lead.ts.isoformat(sep=" ", timespec="seconds"),
                "tg_id": user.tg_id,
                "username": user.username,
                "name": user.name,
                "channel": lead.channel,
                "contact": lead.contact,
                "note": lead.note or "",
            }
            for lead, user in q.all()
        ]

    if not rows:
        return await m.answer("Лидов пока нет.")

    # пишем во временный CSV
    fd, path = tempfile.mkstemp(prefix="leads_", suffix=".csv")
    os.close(fd)
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        await m.answer_document(FSInputFile(path), caption=f"Leads: {len(rows)}")
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
