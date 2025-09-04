# app/routers/progress.py
from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

from app.keyboards.menu import main_menu
from app.storage.repo import session_scope
from app.storage.models import User, DrillRun, Drill, TestResult

router = Router(name="progress")

SPARK = "▁▂▃▄▅▆▇█"

def spark(value: int) -> str:
    # value 0..5 → символ
    levels = [0,1,2,3,4,5,6,7]  # на всякий случай
    ix = max(0, min(7, round(value * (len(levels)-1) / 5)))
    return SPARK[ix]

@router.message(StateFilter("*"), F.text == "📈 Мой прогресс")
@router.message(StateFilter("*"), Command("progress"))
@router.message(StateFilter("*"), lambda m: isinstance(m.text, str) and "прогресс" in m.text.lower())
async def show_progress(m: Message):
    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=m.from_user.id).first()
        if not u:
            await m.answer("Сначала /start.", reply_markup=main_menu())
            return
        runs = (s.query(DrillRun).filter_by(user_id=u.id)
                .order_by(DrillRun.ts.desc()).limit(3).all())
        # тайтлы этюдов
        last = []
        for r in runs:
            d = s.query(Drill).filter_by(id=r.drill_id).first()
            if d:
                last.append(d.payload_json.get("title", r.drill_id))
        # профиль по последнему тесту
        tr = (s.query(TestResult).filter_by(user_id=u.id)
              .order_by(TestResult.ts.desc()).first())

    axes_txt = "нет данных (пройдите 🎭 Мини-кастинг)" if not tr else (
        "Внимание {0} {5}\nПауза {1} {6}\nТемп {2} {7}\nИнтонация {3} {8}\nЛогика {4} {9}".format(
            tr.axes_json.get("attention",0),
            tr.axes_json.get("pause",0),
            tr.axes_json.get("tempo",0),
            tr.axes_json.get("intonation",0),
            tr.axes_json.get("logic",0),
            spark(tr.axes_json.get("attention",0)),
            spark(tr.axes_json.get("pause",0)),
            spark(tr.axes_json.get("tempo",0)),
            spark(tr.axes_json.get("intonation",0)),
            spark(tr.axes_json.get("logic",0)),
        )
    )
    last_txt = "— нет записей" if not last else "• " + "\n• ".join(last)
    msg = (
        f"Стрик: {u.streak}\n\n"
        f"Последние этюды:\n{last_txt}\n\n"
        f"Профиль 5 осей:\n{axes_txt}"
    )
    await m.answer(msg, reply_markup=main_menu())
