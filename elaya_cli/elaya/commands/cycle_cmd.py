from __future__ import annotations

from typing import Any, Dict
import json
import os

import requests
import typer

# Базовый URL web-core
CORE_URL = os.getenv("ELAYA_CORE_URL", "https://elaya-stagecoach-web.onrender.com").rstrip("/")
TIMEOUT = 10


def _fetch_cycle_state() -> Dict[str, Any]:
    """
    Запросить высокоуровневое состояние цикла у web-core.
    """
    url = f"{CORE_URL}/api/cycle/state"
    resp = requests.get(url, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def _print_cycle_state(cycle_state: Dict[str, Any]) -> None:
    """
    Красиво вывести состояние цикла.
    """
    cycle_num = cycle_state.get("cycle", 0)
    phase = cycle_state.get("phase", "idle")
    last_update = cycle_state.get("last_update", "-")

    typer.echo("🔁  Состояние цикла Элайи")
    typer.echo(f"  • Цикл: {cycle_num}")
    typer.echo(f"  • Фаза: {phase}")
    typer.echo(f"  • Обновлено: {last_update}")


def cycle() -> None:
    """
    Показать состояние цикла Элайи (для CLI).
    """
    try:
        data = _fetch_cycle_state()
    except Exception as exc:
        typer.echo(f"⚠️ Ошибка запроса /api/cycle/state: {exc}")
        raise typer.Exit(code=1)

    if not data.get("ok"):
        typer.echo(f"⚠️ Ядро ответило без ok=true: {data}")
        raise typer.Exit(code=1)

    cycle_state: Dict[str, Any] = data.get("cycle", {}) or {}

    _print_cycle_state(cycle_state)
    typer.echo()
    typer.echo("Полное состояние:")
    typer.echo(json.dumps(cycle_state, ensure_ascii=False, indent=2))


def next() -> None:
    """
    Попросить ядро перейти к следующему шагу цикла (если endpoint поддерживается)
    и вывести обновлённое состояние.
    """
    url = f"{CORE_URL}/api/cycle/next"

    try:
        resp = requests.post(url, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        typer.echo(f"⚠️ Ошибка запроса /api/cycle/next: {exc}")
        raise typer.Exit(code=1)

    if not data.get("ok"):
        typer.echo(f"⚠️ Ядро ответило без ok=true: {data}")
        raise typer.Exit(code=1)

    cycle_state: Dict[str, Any] = data.get("cycle", {}) or {}

    typer.echo("⏭  Переход к следующему шагу цикла выполнен")
    _print_cycle_state(cycle_state)
    typer.echo()
    typer.echo("Полное состояние:")
    typer.echo(json.dumps(cycle_state, ensure_ascii=False, indent=2))
