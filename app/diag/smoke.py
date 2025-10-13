# app/diag/smoke.py
"""
Дым-тест импортов. Запуск:
python -m app.diag.smoke
"""
from __future__ import annotations

import importlib

MODULES = [
    "app.storage.repo",
    "app.main",                 # лишь на импорт, main() НЕ вызываем
    "app.routers.casting",
    "app.routers.entrypoints",
    "app.routers.progress",
    "app.routers.devops_sync",
]

def main() -> None:
    for m in MODULES:
        importlib.invalidate_caches()
        importlib.import_module(m)
        print(f"[OK] import {m}")

if __name__ == "__main__":
    main()
