# app/services/scoring.py
from __future__ import annotations
from dataclasses import dataclass

AXES = ["attention", "pause", "tempo", "intonation", "logic"]

@dataclass
class Question:
    id: str
    text: str
    kind: str           # "fact_manip" | "tempo_pause" | "yn"
    options: list[str]  # варианты на кнопках
    axis_map: dict[str, dict[str, int]]  # {axis: {option_text: +1/0/-1}}

def questions() -> list[Question]:
    q: list[Question] = [
        Question("q1", "Высказывание похоже на факт или на манипуляцию?",
                 "fact_manip", ["Факт", "Манипуляция"],
                 {"logic": {"Факт": 1, "Манипуляция": 0}}),

        Question("q2", "Темп ближе к 70% или быстрее нормы?",
                 "tempo_pause", ["70%", "Быстрее"],
                 {"tempo": {"70%": 1, "Быстрее": 0}}),

        Question("q3", "Есть ли пауза перед репликой?",
                 "yn", ["Да", "Нет"],
                 {"pause": {"Да": 1, "Нет": 0}}),

        Question("q4", "Голос стал теплее/ниже или выше/зажат?",
                 "yn", ["Теплее/ниже", "Выше/зажат"],
                 {"intonation": {"Теплее/ниже": 1, "Выше/зажат": 0}}),

        Question("q5", "Смотришь на партнёра вниманием?",
                 "yn", ["Да", "Нет"],
                 {"attention": {"Да": 1, "Нет": 0}}),

        Question("q6", "Смысл реплики понятен?",
                 "yn", ["Да", "Нет"],
                 {"logic": {"Да": 1, "Нет": 0}}),

        Question("q7", "Темп ровный?",
                 "yn", ["Да", "Нет"],
                 {"tempo": {"Да": 1, "Нет": 0}}),

        Question("q8", "Паузы живые (не механические)?",
                 "yn", ["Да", "Нет"],
                 {"pause": {"Да": 1, "Нет": 0}}),

        Question("q9", "Голос адресный (внимание на партнёре)?",
                 "yn", ["Да", "Нет"],
                 {"attention": {"Да": 1, "Нет": 0}}),

        Question("q10","Интонация опирается на действие, а не на эмоцию?",
                 "yn", ["Да", "Нет"],
                 {"intonation": {"Да": 1, "Нет": 0}}),
    ]
    return q

def score_answers(answers: dict[str, str]) -> dict[str, int]:
    """answers: {question_id: chosen_option} → оси 0..5 (int)."""
    # накопим сырые очки
    raw = {a: 0 for a in AXES}
    qs = {q.id: q for q in questions()}
    for qid, opt in answers.items():
        q = qs.get(qid)
        if not q: 
            continue
        for axis, contribs in q.axis_map.items():
            raw[axis] += int(contribs.get(opt, 0))

    # максимально возможные очки по каждой оси (для нормализации)
    max_axis = {a: 0 for a in AXES}
    for q in qs.values():
        for axis, contribs in q.axis_map.items():
            max_axis[axis] += max(contribs.values()) if contribs else 0

    # нормализуем в 0..5
    out = {}
    for axis in AXES:
        mx = max(1, max_axis[axis])
        val = raw[axis] * 5 / mx
        out[axis] = int(round(val))
        if out[axis] > 5: out[axis] = 5
        if out[axis] < 0: out[axis] = 0
    return out

def recommend_drills(axes: dict[str, int]) -> list[str]:
    rec: list[str] = []
    if axes.get("pause", 5) < 3:
        rec.append("pause_4262")
    if axes.get("attention", 5) < 3:
        rec += ["partner_lighthouse", "volume_4m_dome"]
    # уникальные и не более 2-3
    uniq = []
    for d in rec:
        if d not in uniq:
            uniq.append(d)
    return uniq[:3]
