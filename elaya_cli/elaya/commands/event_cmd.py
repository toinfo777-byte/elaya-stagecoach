# elaya_cli/elaya/commands/event_cmd.py

from __future__ import annotations

import os
from typing import Any, Dict

import requests
import typer
from rich.console import Console
from rich.table import Table

console = Console()


def _get_core_url() -> str:
    """
    Берём URL ядра из переменной ELAYA_CORE_URL.
    Пример: https://elaya-stagecoach-web.onrender.com
    """
    base = os.getenv("ELAYA_CORE_URL", "").strip()
    if not base:
        console.print(
            "[red]Не задана переменная окружения ELAYA_CORE_URL.[/]\n"
            "Пример:\n"
            '  setx ELAYA_CORE_URL "https://elaya-stagecoach-web.onrender.com"'
        )
        raise typer.Exit(code=1)

    return base.rstrip("/")


def _guard_headers() -> Dict[str, str]:
    """
    Если задан ELAYA_GUARD_KEY или GUARD_KEY — добавляем X-Guard-Key.
    Это стыкуется с _check_guard в app/routes/system.py.
    """
    key = os.getenv("ELAYA_GUARD_KEY", "").strip() or os.getenv("GUARD_KEY", "").strip()
    if not key:
        return {}
    return {"X-Guard-Key": key}


def event(
    text: str = typer.Argument(
        ...,
        metavar="TEXT",
        help="Текст события, который попадёт в таймлайн.",
    ),
    scene: str = typer.Option(
        "manual",
        "--scene",
        "-s",
        help="Сцена/тип события (manual, intro, reflect, transition и т.п.).",
    ),
    source: str = typer.Option(
        "cli",
        "--source",
        "-S",
        help='Источник события (по умолчанию "cli").',
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Показать полный ответ сервера.",
    ),
) -> None:
    """
    Отправить произвольное событие в ядро Элайи.

    Пример:
      elaya3 event "Первое событие из CLI"
      elaya3 event "Вход в тренировку" --scene intro
    """
    core_url = _get_core_url()
    url = f"{core_url}/api/event"

    body: Dict[str, Any] = {
        "source": source,
        "scene": scene,
        "payload": {"text": text},
    }

    try:
        resp = requests.post(url, json=body, headers=_guard_headers(), timeout=10)
    except requests.RequestException as exc:
        console.print(f"[red]Ошибка запроса к ядру:[/] {exc}")
        raise typer.Exit(code=1)

    if resp.status_code != 200:
        console.print(
            f"[red]Сервер вернул ошибку {resp.status_code}[/]: {resp.text}"
        )
        raise typer.Exit(code=1)

    data = resp.json()

    if not data.get("ok"):
        console.print(f"[red]Ответ ядра без ok=true:[/] {data}")
        raise typer.Exit(code=1)

    event_data = data.get("event", {})

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Поле")
    table.add_column("Значение", overflow="fold")

    table.add_row("ts", str(event_data.get("ts")))
    table.add_row("cycle", str(event_data.get("cycle")))
    table.add_row("source", str(event_data.get("source")))
    table.add_row("scene", str(event_data.get("scene")))
    table.add_row("payload", str(event_data.get("payload")))

    console.print("[green]Событие отправлено в ядро.[/]")
    console.print(table)

    if verbose:
        console.print("\n[dim]Полный ответ:[/]")
        console.print(data)
