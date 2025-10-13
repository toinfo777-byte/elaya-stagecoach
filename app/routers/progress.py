# app/routers/progress.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

# Кнопка может отсутствовать в некоторых сборках — делаем безопасно
try:
    from app.keyboards.reply import BTN_PROGRESS, main_menu_kb
except Exception:
    BTN_PROGRESS = "📈 Мой прогресс"
    def main_menu_kb():
        return None  # без клавы тоже ок

# Лёгкий доступ к репозиторию прогресса
try:
    # ожидаем, что в app.storage.repo есть синглтон progress и ensure_schema уже вызван в main.py
    from app.storage.repo import progress as progress_repo
except Exception:
    progress_repo = None  # не роняем импорт — вернём заглушку

router = Router(name="progress")


def _sparkline(days):
    """
    Простейшая визуализация за 7 дней:
    0 — '□', >=1 — '■'
    """
    blocks = []
    for d, cnt in days:
        blocks.append("■" if cnt > 0 else "□")
    return "".join(blocks)


async def _render_progress(m: Message) -> None:
    if progress_repo is None:
        await m.answer("Прогресс пока недоступен. Попробуй позже.")
        return

    try:
        s = await progress_repo.get_summary(user_id=m.from_user.id)
    except Exception:
        await m.answer("Не удалось загрузить прогресс. Попробуй позже.")
        return

    days_vis = _sparkline(s.last_days)
    txt = (
        "📈 Твой прогресс за 7 дней\n"
        f"Стрик: <b>{s.streak}</b> дней\n"
        f"Эпизодов: <b>{s.episodes_7d}</b>\n"
        f"Очков: <b>{s.points_7d}</b>\n"
        f"{days_vis}  (последние 7 дней)\n\n"
        "Продолжай — даже маленький шаг сегодня держит стрик живым."
    )
    await m.answer(txt, reply_markup=main_menu_kb())


@router.message(Command("progress"))
async def cmd_progress(m: Message) -> None:
    await _render_progress(m)


@router.message(F.text == BTN_PROGRESS)
async def btn_progress(m: Message) -> None:
    await _render_progress(m)


__all__ = ["router"]
