from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import typer

from .core.api_client import get_core_status
from .commands.event_cmd import event as event_command
from .commands.intro_cmd import intro as intro_command
from .commands.reflect_cmd import reflect as reflect_command
from .commands.transition_cmd import transition as transition_command
from .commands.cycle_cmd import cycle as cycle_command
from .commands.cycle_cmd import next

CLI_VERSION = "0.5.0"

app = typer.Typer(help="Локальный CLI-агент Элайи")


# ------ базовые команды ------


@app.command()
def status() -> None:
    """
    Показать локальный статус CLI-агента и краткий статус web-core.
    """
    root = Path(__file__).resolve().parents[2]

    typer.echo(f"Elaya CLI Agent v{CLI_VERSION}")
    typer.echo("Status: OK")
    typer.echo(f"Time: {datetime.now().isoformat(timespec='seconds')}")
    typer.echo(f"Root: {root}")

    try:
        core = get_core_status()
    except Exception as exc:
        typer.echo(f"⚠ Ошибка запроса /api/status: {exc}")
        return

    typer.echo("\nCore status (/api/status):")
    typer.echo(json.dumps(core, ensure_ascii=False, indent=2))


@app.command()
def sync() -> None:
    """
    Принудительно дернуть /api/status и вывести полный JSON.
    Удобно для отладки связи CLI ↔ web-core.
    """
    try:
        core = get_core_status()
    except Exception as exc:
        typer.echo(f"⚠ Ошибка запроса к web-core: {exc}")
        raise typer.Exit(code=1)

    typer.echo(json.dumps(core, ensure_ascii=False, indent=2))


# ------ высокоуровневые команды ------

# ручное событие
app.command(name="event")(event_command)

# фазы цикла (ручной режим)
app.command(name="intro")(intro_command)
app.command(name="reflect")(reflect_command)
app.command(name="transition")(transition_command)
app.command(name="cycle")(cycle_command)


# автоматический Cycle Engine
app.command(name="next")(next)


def main() -> None:
    """
    Точка входа для console_script (elaya3).
    """
    app()
