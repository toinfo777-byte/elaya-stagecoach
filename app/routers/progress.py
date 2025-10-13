# app/routers/progress.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

# Безопасные импорты кнопки и клавиатуры
try:
    from app.keyboards.reply import BTN_PROGRESS, main_menu_kb
except Exception:
    BTN_PROGRESS = "📈 Мой прогресс"
    def main_menu_kb():
        # Можно вернуть пустую клавиатуру — не критично
        return None

# Пытаемся подтянуть репозиторий прогресса
try:
    from app.storage.repo import progress as progress_repo
except Exception:
    progress_repo = None  # не роняем импорт — покажем заглушку

router = Router(name="progress")


def _sparkline(days):
    """Простейшая визуализация за 7 дней: 0 → '□', >=1 → '■'."""
    return "".join("■" if cnt > 0 else "□" for _, cnt in days)


async def _render_progress(m: Message) -> None:
    if not progress_repo:
        await m.answer("Прогресс пока недоступен. Попробуй позже.")
        return

    try:
        s = await progress_repo.get_summary(user_id=m.from_user.id)
    except Exception:
        await m.answer("Не удалось загрузить прогресс. Попробуй позже.")
        return

    txt = (
        "📈 Твой прогресс за 7 дней\n"
        f"Стрик: <b>{s.streak}</b> дней\n"
        f"Эпизодов: <b>{s.episodes_7d}</b>\n"
        f"Очков: <b>{s.points_7d}</b>\n"
        f"{_sparkline(s.last_days)}"
    )
    await m.answer(txt, reply_markup=main_menu_kb())


@router.message(Command("progress"))
async def cmd_progress(m: Message) -> None:
    await _render_progress(m)


@router.message(F.text == BTN_PROGRESS)
async def btn_progress(m: Message) -> None:
    await _render_progress(m)


# Алиас на всякий случай — чтобы можно было импортировать как progress_router
progress_router = router

__all__ = ["router", "progress_router"]
