from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.keyboards.menu import main_menu
from app.storage.repo import session_scope, log_event
from app.storage.models import User

router = Router(name="feedback")

# Поддерживаем все старые форматы callback_data
_EMOJI_ALIASES = {
    "🔥": "fire", "👌": "ok", "😐": "meh",
    "fire": "fire", "hot": "fire",
    "ok": "ok", "like": "ok",
    "meh": "meh", "neutral": "meh", "dislike": "meh",
    "fb_fire": "fire", "fb_ok": "ok", "fb_meh": "meh",
}

class OnePhrase(StatesGroup):
    awaiting = State()

def _parse_feedback_cb(data: str) -> dict:
    """
    Возвращает словарь:
      {kind: 'emoji'|'phrase', value: 'fire'|'ok'|'meh'|None, category: str|None, target_id: str|None}
    Понимает:
      - 'fb:emoji:fire|cat:training|id:123'
      - 'emoji:ok', 'fb:phrase', 'feedback:phrase', 'phrase'
      - 'fire', 'ok', 'meh', 'fb_fire', 'fb:meh' и пр.
    """
    out = {"kind": None, "value": None, "category": None, "target_id": None}
    s = (data or "").strip()

    # разбиваем по |
    parts = s.split("|") if "|" in s else [s]
    for part in parts:
        part = part.strip()

        # cat:/id:
        if part.startswith(("cat:", "category:")):
            out["category"] = part.split(":", 1)[1]
            continue
        if part.startswith("id:"):
            out["target_id"] = part.split(":", 1)[1]
            continue

        # составные метки fb:...:...
        if ":" in part:
            toks = part.split(":")
            # варианты: fb:emoji:fire / feedback:phrase / review:emoji:ok / emoji:meh
            if toks[-1] in _EMOJI_ALIASES:
                out["kind"] = "emoji"
                out["value"] = _EMOJI_ALIASES[toks[-1]]
                continue
            if "phrase" in toks:
                out["kind"] = "phrase"
                continue

        # простые токены
        if part in _EMOJI_ALIASES:
            out["kind"] = "emoji"
            out["value"] = _EMOJI_ALIASES[part]
            continue
        if part in {"phrase", "fb_phrase", "fb:phrase"}:
            out["kind"] = "phrase"
            continue

    return out

# ——— ЕДИНЫЙ обработчик всех колбэков отзывов ———
@router.callback_query(
    F.data.startswith(("fb", "feedback", "review", "emoji", "phrase")) |
    F.data.in_(set(_EMOJI_ALIASES.keys()))
)
async def feedback_router(cb: CallbackQuery, state: FSMContext):
    info = _parse_feedback_cb(cb.data)

    # Если «1 фраза» — запускаем FSM
    if info["kind"] == "phrase":
        await state.update_data(fb_category=info["category"], fb_target_id=info["target_id"])
        await state.set_state(OnePhrase.awaiting)
        await cb.answer()
        await cb.message.answer(
            "Напишите одной короткой фразой (до 200 символов). Если передумали — отправьте /cancel.",
            reply_markup=main_menu()
        )
        return

    # Если эмодзи — просто подтвердим и залогируем
    if info["kind"] == "emoji" and info["value"] in {"fire", "ok", "meh"}:
        try:
            with session_scope() as s:
                u = s.query(User).filter_by(tg_id=cb.from_user.id).first()
                if u:
                    log_event(s, u.id, "feedback_emoji", {
                        "value": info["value"],
                        "category": info["category"],
                        "target_id": info["target_id"],
                    })
                    s.commit()
        except Exception:
            pass
        await cb.answer("Принял. Спасибо! 👍", show_alert=False)
        return

    # Не распознали — молча закрываем
    await cb.answer()

@router.message(OnePhrase.awaiting, ~F.text.startswith("/"))
async def feedback_phrase_save(m: Message, state: FSMContext):
    text = (m.text or "").strip()
    if not text:
        await m.answer("Пусто. Напишите короткую фразу до 200 символов.")
        return
    if len(text) > 200:
        await m.answer(f"Слишком длинно ({len(text)} симв.). Сократите до 200.")
        return

    d = await state.get_data()
    try:
        with session_scope() as s:
            u = s.query(User).filter_by(tg_id=m.from_user.id).first()
            if u:
                log_event(s, u.id, "feedback_phrase", {
                    "text": text,
                    "category": d.get("fb_category"),
                    "target_id": d.get("fb_target_id"),
                })
                s.commit()
    except Exception:
        pass

    await state.clear()
    await m.answer("Спасибо! Сохранил ✍️", reply_markup=main_menu())

@router.message(OnePhrase.awaiting, F.text == "/cancel")
async def feedback_phrase_cancel(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("Отменено. Возвращаю в меню.", reply_markup=main_menu())
