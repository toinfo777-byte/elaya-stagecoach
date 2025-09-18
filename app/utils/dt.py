# app/utils/dt.py
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo


def fmt_local(
    dt_utc: datetime,
    tz: str | None,
    fallback_tz: str = "Europe/Moscow",
    fmt: str = "%d.%m %H:%M",
) -> str:
    """
    Переводит UTC-время в локальное и форматирует.
    Если tz сломан/пуст — используем fallback_tz.
    """
    try:
        src = dt_utc.replace(tzinfo=ZoneInfo("UTC"))
        dst_tz = ZoneInfo(tz or fallback_tz)
        return src.astimezone(dst_tz).strftime(fmt)
    except Exception:
        # на всякий случай не падаем ни при каких обстоятельствах
        return dt_utc.strftime(fmt)
