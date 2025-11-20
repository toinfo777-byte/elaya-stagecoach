import typer

from ..core.state import get_project_info
from ..core.logger import log_event


def run() -> None:
    info = get_project_info()

    typer.echo("Project info:")
    typer.echo(f"  Root:  {info.root}")

    if info.docs_dir:
        typer.echo(f"  Docs:  {info.docs_dir}")
    else:
        typer.echo("  Docs:  (not found)")

    if info.app_dir:
        typer.echo(f"  App:   {info.app_dir}")
    else:
        typer.echo("  App:   (not found)")

    log_event(
        event="command=project",
        ok=True,
        extra={"root": str(info.root)},
    )
