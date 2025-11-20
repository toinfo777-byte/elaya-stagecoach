from __future__ import annotations

from pathlib import Path
from datetime import datetime
import json
from typing import Any, Dict, Optional

from .config import APP_NAME
from . import api_client


# ~/.elaya/pulse_log
PULSE_DIR = Path.home() / ".elaya"
PULSE_FILE = PULSE_DIR / "pulse_log"

PULSE_DIR.mkdir(parents=True, exist_ok=True)


def log_event(event: str, ok: bool = True, extra: Optional[Dict[str, Any]] = None) -> None:
    """
    Пишет событие в локальный лог (микро-Pulse) и,
    если возможно, отправляет его в web-core.
    """
    ts = datetime.now().isoformat(timespec="seconds")
    extra = extra or {}

    # 1) Локальный лог-файл
    line = f"{ts} event={event} ok={str(ok).lower()} extra={json.dumps(extra, ensure_ascii=False)}"
    try:
        with PULSE_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        # Локальный лог не должен ломать работу агента
        pass

    # 2) Отправка в web-core (если настроен)
    try:
        if api_client.is_configured():
            api_client.send_pulse(event=event, ok=ok, extra=extra)
    except Exception:
        # Сетевые ошибки тоже заглатываем — агент должен жить.
        pass
