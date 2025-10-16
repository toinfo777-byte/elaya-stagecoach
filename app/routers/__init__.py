# app/routers/__init__.py
# Явно импортируем все подмодули и выставляем их в __all__,
# чтобы `from app.routers import <name>` всегда работало.

from . import (
    entrypoints,
    help,
    aliases,
    onboarding,
    system,
    minicasting,
    leader,
    training,
    progress,
    privacy,
    settings as settings_router,
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
    "aliases",
    "onboarding",
    "system",
    "minicasting",
    "leader",
    "training",
    "progress",
    "privacy",
    "settings_router",
    "extended",
    "casting",
    "apply",
    "faq",
    "devops_sync",
    "diag",
    "panic",
]

