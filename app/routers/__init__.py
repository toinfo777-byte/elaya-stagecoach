# app/routers/__init__.py
# Централизованный экспорт всех роутеров.
# Если какого-то файла нет — ничего страшного, main.py подключает их безопасно.

from . import (
    entrypoints,
    help,
    onboarding,
    system,
    minicasting,
    leader,
    training,
    progress,
    privacy,
    settings,
    extended,
    casting,
    apply,
    faq,
    devops_sync,
    diag,
    panic,
)

__all__ = [
    "entrypoints",
    "help",
    "onboarding",
    "system",
    "minicasting",
    "leader",
    "training",
    "progress",
    "privacy",
    "settings",
    "extended",
    "casting",
    "apply",
    "faq",
    "devops_sync",
    "diag",
    "panic",
]
