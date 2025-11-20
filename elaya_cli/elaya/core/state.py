# elaya/core/state.py

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import sys
import os

from .config import PROJECT_ROOT, APP_NAME, APP_VERSION


@dataclass
class ElayaStatus:
    status: str
    now: datetime
    project_root: Path
    app_name: str = APP_NAME
    app_version: str = APP_VERSION


@dataclass
class ElayaProjectInfo:
    root: Path
    docs_dir: Path | None = None
    app_dir: Path | None = None


@dataclass
class ElayaDiagInfo:
    python_version: str
    venv: str | None
    project_root: Path
    warnings: list[str] = field(default_factory=list)


# --- публичные функции состояния ---


def get_status() -> ElayaStatus:
    """Текущее состояние агента."""
    return ElayaStatus(
        status="OK",
        now=datetime.now(),
        project_root=PROJECT_ROOT,
    )


def get_project_info() -> ElayaProjectInfo:
    """Информация о локальном проекте Элайи.

    Сейчас — простое предположение:
    - docs/  рядом с корнем
    - app/   рядом с корнем
    """
    docs = PROJECT_ROOT / "docs"
    app = PROJECT_ROOT / "app"

    return ElayaProjectInfo(
        root=PROJECT_ROOT,
        docs_dir=docs if docs.exists() else None,
        app_dir=app if app.exists() else None,
    )


def get_diag_info() -> ElayaDiagInfo:
    """Облегчённая диагностика (v0.3).

    Без CPU/памяти, только:
    - версия Python
    - активный venv (если есть)
    - корень проекта
    - простые предупреждения
    """
    warnings: list[str] = []

    python_version = sys.version.split()[0]

    venv = os.environ.get("VIRTUAL_ENV")
    if not venv:
        warnings.append("virtualenv_not_active")

    if not PROJECT_ROOT.exists():
        warnings.append("project_root_missing")

    return ElayaDiagInfo(
        python_version=python_version,
        venv=venv,
        project_root=PROJECT_ROOT,
        warnings=warnings,
    )
