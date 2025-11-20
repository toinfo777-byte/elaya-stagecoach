import typer

from ..core.state import get_diag_info
from ..core.logger import log_event


def run() -> None:
    diag = get_diag_info()

    typer.echo("Diagnostic info (v0.3):")
    typer.echo(f"  Python:  {diag.python_version}")
    typer.echo(f"  Project: {diag.project_root}")

    if diag.venv:
        typer.echo(f"  venv:    {diag.venv}")
    else:
        typer.echo("  venv:    (not active)")

    if diag.warnings:
        typer.echo()
        typer.echo("Warnings:")
        for w in diag.warnings:
            typer.echo(f"  - {w}")
    else:
        typer.echo()
        typer.echo("Warnings: none")

    log_event(
        event="command=diag",
        ok=True,
        extra={"warnings": ",".join(diag.warnings) if diag.warnings else "none"},
    )
