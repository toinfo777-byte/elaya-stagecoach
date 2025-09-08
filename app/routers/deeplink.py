from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.storage.repo import session_scope, log_event
from app.storage.models import User
from app.routers.training import training_entry
from app.routers.casting import casting_entry

router = Router(name="deeplink")

@router.message(F.text.regexp(r"^/start(\s+.+)?$"))
async def start_with_payload(m: Message, state: FSMContext):
    parts = m.text.split(maxsplit=1)
    payload = (parts[1] if len(parts) > 1 else "").strip()

    if payload not in {"go_training", "go_casting", "coach"}:
        return  # пусть обработает твой обычный /start (онбординг)

    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=m.from_user.id).first()
        uid = u.id if u else None
        # не перетираем first_source, только last_source:
        if u and not u.source:
            u.source = payload
        if u:
            u.last_source = payload
            s.commit()
        log_event(s, uid, f"start_{payload}", {"chat_id": m.chat.id})

    if payload == "go_training":
        await training_entry(m, state)
    elif payload == "go_casting":
        await casting_entry(m, state)
    else:  # coach
        from app.routers.coach import coach_on
        await coach_on(m)  # эквивалент /coach_on
