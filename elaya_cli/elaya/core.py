# core.py — ядро Элайя-Агента v0.1

import os
import datetime


def get_status():
    """Возвращает базовую информацию о локальном состоянии Элайи."""
    now = datetime.datetime.now()

    return {
        "status": "OK",
        "time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "cwd": os.getcwd(),
    }
