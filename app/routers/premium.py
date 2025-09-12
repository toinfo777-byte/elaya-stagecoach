from aiogram import Router, F
from aiogram.types import Message

router = Router(name="premium")

def _contains(substr: str):
    return F.text.func(lambda t: isinstance(t, str) and substr.lower() in t.lower())

# ===== Команда /premium и кнопка «Расширенная версия» =====
@router.message(F.text == "/premium")
@router.message(_contains("Расширенная версия"))
async def premium_info(msg: Message):
    await msg.answer(
        "⭐ Расширенная версия\n\n"
        "• Больше сценариев тренировки\n"
        "• Персональные разборы\n"
        "• Расширенная метрика прогресса\n\n"
        "Пока это превью. Если интересно — напиши «Хочу расширенную» или жми /menu."
    )

# (опционально) быстрый хендлер на «Хочу расширенную»
@router.message(_contains("Хочу расширенную"))
async def premium_lead(msg: Message):
    await msg.answer(
        "🔥 Супер! Мы свяжемся с тобой по контактам из анкеты. "
        "Если хочешь — оставь email или напиши /menu."
    )
