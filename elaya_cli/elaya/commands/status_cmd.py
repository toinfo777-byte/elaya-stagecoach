import typer

from ..core.state import get_status
from ..core.logger import log_event


def run() -> None:
    st = get_status()

    typer.echo("Status: OK")
    typer.echo(f"Time:   {st.now.isoformat(sep=' ', timespec='seconds')}")
    typer.echo(f"Root:   {st.project_root}")
    typer.echo(f"App:    {st.app_name} v{st.app_version}")

    log_event(
        event="command=status",
        ok=True,
        extra={"project": str(st.project_root)},
    )
