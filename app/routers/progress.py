# app/routers/progress.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

# Безопасные импорты UI
try:
    from app.keyboards.reply import BTN_PROGRESS, main_menu_kb
except Exception:
    BTN_PROGRESS = "📈 Мой прогресс"
    def main_menu_kb():
        return None

# Пытаемся взять реальный репозиторий прогресса; иначе — заглушка
try:
    from app.storage.repo import progress as _progress_repo  # ProgressRepo singleton
except Exception:
    _progress_repo = None

router = Router(name="progress")


async def _get_summary(user_id: int):
    """
    Унифицированный доступ к сводке прогресса.
    Ожидаемый интерфейс ProgressRepo.get_summary(user_id=...)
    """
    if _progress_repo is None:
        # Заглушка на случай отсутствия хранилища
        class _Dummy:
            async def get_summary(self, *, user_id: int):
                from dataclasses import dataclass
                from typing import List, Tuple
                @dataclass
                class Summary:
                    streak: int
                    episodes_7d: int
                    points_7d: int
                    last_days: List[Tuple[str, int]]
                return Summary(streak=0, episodes_7d=0, points_7d=0, last_days=[])
        return await _Dummy().get_summary(user_id=user_id)
    return await _progress_repo.get_summary(user_id=user_id)


def _format_summary(s) -> str:
    # s.last_days: [(YYYY-MM-DD, count)]
    days_lines = []
    for d, c in (s.last_days or []):
        box = "■" if c > 0 else "□"
        days_lines.append(f"{d}: {box} x{c}")
    days_block = "\n".join(days_lines) if days_lines else "Нет активностей за 7 дней."

    return (
        "📈 <b>Твой прогресс</b>\n\n"
        f"🔥 Серия по дням: <b>{s.streak}</b>\n"
        f"✅ Эпизодов за 7 дней: <b>{s.episodes_7d}</b>\n"
        f"⭐️ Баллов за 7 дней: <b>{s.points_7d}</b>\n\n"
        f"{days_block}\n\n"
        "Продолжай! Любая короткая тренировка засчитывается."
    )


@router.message(Command("progress"))
@router.message(F.text == BTN_PROGRESS)
async def show_progress(m: Message):
    summary = await _get_summary(m.from_user.id)
    await m.answer(_format_summary(summary), reply_markup=main_menu_kb())


# Алиас на всякий случай
progress_router = router
__all__ = ["router", "progress_router", "show_progress"]
