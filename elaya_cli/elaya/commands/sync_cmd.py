from __future__ import annotations

import typer

from ..core.api_client import ping_core
from ..core.logger import log_event


def run() -> None:
    """
    Попытка синхронизации с web-core.
    """
    ok, message = ping_core()

    if ok:
        typer.echo(f"Sync: OK — {message}")
    else:
        typer.echo(f"Sync: FAILED — {message}")

    log_event(
        event="sync",
        ok=ok,
        extra={"message": message},
    )
