# trainer/app/training_progress.py
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

# ------------------------------
# ХРАНИЛИЩЕ
# ------------------------------

DATA_FILE = Path(__file__).with_name("training_records.json")


def _load() -> List[Dict[str, Any]]:
    """
    Загружаем весь список тренировок.
    Если файла нет — возвращаем пустой список.
    """
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception:
        # на всякий случай не ломаемся от битого файла
        return []


def _save(records: List[Dict[str, Any]]) -> None:
    """
    Сохраняем все тренировочные записи.
    """
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


# ------------------------------
# ЗАПИСЬ ТРЕНИРОВКИ (НОВЫЙ API)
# ------------------------------

def register_training(
    *,
    user_id: int,
    date: date,
    vector: str,
    reflect: str,
    transition: str,
    review: Optional[str] = None,
) -> None:
    """
    Регистрирует завершённую Тренировку Дня.

    review — НЕобязательный параметр.
    Если он не передан — запись остаётся валидной.
    """
    record: Dict[str, Any] = {
        "user_id": user_id,
        "date": date.isoformat(),
        "vector": vector,
        "reflect": reflect,
        "transition": transition,
    }

    if review is not None:
        record["review"] = review

    records = _load()
    records.append(record)
    _save(records)


def _calc_streak(records: List[Dict[str, Any]]) -> int:
    """
    Очень простая «серия по дням»:
    считаем количество уникальных дат, когда были тренировки.
    (Пока без сложной логики подряд и пропусков.)
    """
    dates = {r.get("date") for r in records if r.get("date")}
    return len(dates)


def get_overview(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Возвращает сводку по тренировкам пользователя:
    - total: всего завершено тренировок
    - streak: сколько дней с тренировками (упрощённая серия)
    - last: словарь с последней тренировкой (date, vector, reflect, transition, review?)
    """
    records = [r for r in _load() if r.get("user_id") == user_id]
    if not records:
        return None

    # сортируем по дате (она лежит в ISO-формате)
    records_sorted = sorted(records, key=lambda r: r.get("date", ""), reverse=True)
    last = records_sorted[0]

    overview: Dict[str, Any] = {
        "total": len(records),
        "streak": _calc_streak(records),
        "last": last,
    }
    return overview


# ------------------------------
# СТАРЫЙ IN-MEMORY API (для совместимости)
# ------------------------------

_USER_STATS: Dict[int, Dict[str, Any]] = {}


def _ensure_user(user_id: int) -> Dict[str, Any]:
    if user_id not in _USER_STATS:
        _USER_STATS[user_id] = {
            "total": 0,
            "by_date": {},
        }
    return _USER_STATS[user_id]


async def register_training_simple(user_id: int) -> None:
    """
    Старый in-memory регистратор.
    Работает параллельно с файловым хранилищем.
    """
    stats = _ensure_user(user_id)
    stats["total"] += 1
    today = date.today().isoformat()
    stats["by_date"][today] = stats["by_date"].get(today, 0) + 1


def get_stats(user_id: int) -> Dict[str, Any]:
    """
    Возвращает очень простую статистику in-memory.
    Это сохраняем для старых обработчиков.
    """
    return _ensure_user(user_id).copy()
