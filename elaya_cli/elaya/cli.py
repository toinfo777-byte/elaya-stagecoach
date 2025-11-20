# elaya_cli/elaya/cli.py

from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import Any, Dict

import platform
import sys

import typer

from .core.api_client import get_status, send_event
from .core.api_client import get_core_url, CORE_URL_ENV

APP_NAME = "Elaya CLI Agent"
APP_VERSION = "v0.4.1"

app = typer.Typer(help="Локальный CLI-агент Элайи")


# ------------------------ утилиты вывода ------------------------


def _print_header(title: str) -> None:
    typer.echo(f"\n=== {title} ===")


def _now_str() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _project_root() -> Path:
    # корень проекта — одна папка выше текущей (elaya_cli)
    return Path.cwd().resolve().parent


# ----------------------------- status ----------------------------


@app.command()
def status() -> None:
    """
    Показать локальный статус CLI-агента.
    """
    typer.echo(f"Status: OK")
    typer.echo(f"Time:   {_now_str()}")
    typer.echo(f"Root:   {_project_root()}")
    typer.echo(f"App:    {APP_NAME} {APP_VERSION}")


# ------------------------------ diag -----------------------------


@app.command()
def diag() -> None:
    """
    Лёгкая диагностика окружения (Python, переменные).
    """
    _print_header("Python")
    typer.echo(f"  Version: {sys.version.split()[0]}")
    typer.echo(f"  Impl:    {platform.python_implementation()}")
    typer.echo(f"  Exec:    {sys.executable}")

    _print_header("Project")
    typer.echo(f"  Root: { _project_root() }")

    _print_header("Web-core")
    core_url = get_core_url()
    env_val = (
        f"{CORE_URL_ENV}={core_url}"
        if CORE_URL_ENV in sys.environ
        else f"{CORE_URL_ENV} (используется значение по умолчанию)"
    )
    typer.echo(f"  URL:  {core_url}")
    typer.echo(f"  Env:  {env_val}")


# ----------------------------- project ---------------------------


@app.command()
def project() -> None:
    """
    Краткая информация о структуре проекта.
    """
    root = _project_root()
    _print_header("Project structure")
    typer.echo(f"Root: {root}")
    typer.echo("Основные директории:")
    for name in ["app", "elaya_cli", "docker", "docs"]:
        p = root / name
        mark = "[+]" if p.exists() else "[ ]"
        typer.echo(f"  {mark} {name}")


# ------------------------------ sync -----------------------------


@app.command()
def sync() -> None:
    """
    Синхронизация с web-core: проверка /api/status.

    По сути — "ping" ядра Элайи.
    """
    core_url = get_core_url()
    try:
        data: Dict[str, Any] = get_status()
    except Exception as exc:  # noqa: BLE001
        typer.echo(
            f"Sync: FAILED — Ошибка при запросе к web-core "
            f"({core_url}/api/status): {exc}"
        )
        raise typer.Exit(code=1)

    ok = data.get("ok")
    core = data.get("core") or {}
    cycle = core.get("cycle", "?")
    last_update = core.get("last_update", "-")

    if ok:
        typer.echo(
            f"Sync: OK — web-core online, "
            f"cycle={cycle}, last_update={last_update}"
        )
    else:
        typer.echo(
            f"Sync: ответ получен, но ok={ok!r}. "
            f"Данные: {data!r}"
        )


# ------------------------------ event ----------------------------


@app.command()
def event(
    text: str = typer.Argument(..., help="Текст события для Таймлайна."),
    scene: str = typer.Option(
        "manual",
        "--scene",
        "-s",
        help="Тип/сцена события (manual, intro, reflect, transition и т.п.)",
    ),
) -> None:
    """
    Отправить произвольное событие в Таймлайн Элайи (/timeline).

    Пример:
      elaya3 event "Первое событие из CLI"
      elaya3 event "Событие intro" --scene intro
    """
    payload: Dict[str, Any] = {"text": text}

    try:
        data = send_event(source="cli", scene=scene, payload=payload)
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"Event: FAILED — ошибка при отправке события: {exc}")
        raise typer.Exit(code=1)

    evt = (data or {}).get("event", {})
    ts = evt.get("ts", "?")
    typer.echo(f"Event: OK — событие отправлено (scene={scene}, ts={ts})")


# ----------------------------- entrypoint ------------------------


def main() -> None:
    app()


if __name__ == "__main__":
    main()
