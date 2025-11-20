from __future__ import annotations  # самый первый импорт

import typer

from .commands import help_cmd, status_cmd, project_cmd, diag_cmd, sync_cmd
from .core.logger import log_event

# --- Typer-приложение ---

app = typer.Typer(
    add_completion=False,
    help="Elaya CLI Agent — локальный слой присутствия Элайи.",
)

# --- Команды ---

@app.command("help")
def help_command() -> None:
    """Показать список команд Elaya."""
    help_cmd.run()
    log_event(event="command=help", ok=True)


@app.command("status")
def status_command() -> None:
    """Состояние агента и корня проекта."""
    status_cmd.run()
    log_event(event="command=status", ok=True)


@app.command("project")
def project_command() -> None:
    """Информация о структуре проекта."""
    project_cmd.run()
    log_event(event="command=project", ok=True)


@app.command("diag")
def diag_command() -> None:
    """Лёгкая диагностика окружения."""
    diag_cmd.run()
    log_event(event="command=diag", ok=True)


@app.command("sync")
def sync_command() -> None:
    """Попытка синхронизации с web-core (если настроен)."""
    sync_cmd.run()
    log_event(event="command=sync", ok=True)


# --- Точка входа для console_script elaya3 ---

def main() -> None:
    """Entry point для console_script `elaya3`."""
    app()


if __name__ == "__main__":
    main()
