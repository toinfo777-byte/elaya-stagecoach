from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import typer

from .core.api_client import get_core_status
from .commands.event_cmd import event as event_command

CLI_VERSION = "0.4.2"

app = typer.Typer(help="Локальный CLI-агент Элайи")


# ------- команды -------


@app.command()
def status() -> None:
    """
    Показать локальный статус CLI-агента и краткий статус web-core.
    """
    root = Path(__file__).resolve().parents[2]

    typer.echo(f"Status: OK")
    typer.echo(f"Time:   {datetime.now().isoformat(sep=' ', timespec='seconds')}")
    typer.echo(f"Root:   {root}")
    typer.echo(f"App:    Elaya CLI Agent v{CLI_VERSION}")

    typer.echo()
    typer.echo("Core status (/api/status):")

    try:
        data = get_core_status()
    except Exception as exc:
        typer.echo(f"  ⚠️  Ошибка запроса к web-core: {exc}")
        return

    if not data.get("ok"):
        typer.echo(f"  ⚠️  Ответ без ok=true: {data}")
        return

    core = data.get("core", {})
    events = core.get("events", [])

    typer.echo(f"  cycle:       {core.get('cycle')}")
    typer.echo(f"  last_update: {core.get('last_update')}")
    typer.echo(f"  events:      {len(events)}")


@app.command()
def sync() -> None:
    """
    Принудительно дернуть /api/status и вывести полный JSON.
    Удобно для отладки связи CLI ↔ web-core.
    """
    try:
        data = get_core_status()
    except Exception as exc:
        typer.echo(f"⚠️  Ошибка запроса к web-core: {exc}")
        raise typer.Exit(code=1)

    typer.echo(json.dumps(data, ensure_ascii=False, indent=2))


# Подключаем команду event из отдельного модуля.
app.command(name="event")(event_command)


def main() -> None:
    """
    Точка входа для console_script (elaya3).
    """
    app()
