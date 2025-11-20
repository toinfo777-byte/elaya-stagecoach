from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sys
import os


# --- базовые структуры ---


@dataclass
class ElayaStatus:
    status: str
    time: datetime
    folder: Path


@dataclass
class ElayaProjectInfo:
    time: datetime
    root: Path
    docs: Path
    app: Path


@dataclass
class ElayaDiagInfo:
    python: str
    venv: Path | None
    project_root: Path
    warnings: list[str]


# --- базовая логика ---


def load_project_root(start: Path | None = None) -> Path:
    """
    Ищем корень проекта — папку, где лежит .git или файлы проекта.
    Если ничего не нашли, считаем корнем текущую директорию.
    """
    if start is None:
        start = Path.cwd()

    current = start.resolve()
    for parent in [current, *current.parents]:
        if (parent / ".git").exists():
            return parent
    return current


def get_status() -> ElayaStatus:
    root = load_project_root()
    return ElayaStatus(
        status="OK",
        time=datetime.now(),
        folder=root,
    )


def get_project_info() -> ElayaProjectInfo:
    root = load_project_root()
    docs = root / "docs"
    app = root / "app"
    return ElayaProjectInfo(
        time=datetime.now(),
        root=root,
        docs=docs,
        app=app,
    )


def get_diag_info() -> ElayaDiagInfo:
    """
    Минимальная диагностика окружения.
    """
    python = sys.executable
    project_root = load_project_root()

    venv = os.environ.get("VIRTUAL_ENV")
    venv_path = Path(venv) if venv else None

    warnings: list[str] = []
    if not venv_path:
        warnings.append("VIRTUAL_ENV не установлен — возможно, venv не активирован.")

    return ElayaDiagInfo(
        python=python,
        venv=venv_path,
        project_root=project_root,
        warnings=warnings,
    )
