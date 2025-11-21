from __future__ import annotations

from typing import Any, Dict

import typer

from ..core.api_client import send_event


def reflect(
    text: str = typer.Argument(..., help="Текст события для фазы 'reflect'"),
) -> None:
    """
    Отправить событие в фазу reflect (отражение цикла).
    """

    payload: Dict[str, Any] = {"text": text}

    try:
        result = send_event(source="cli", scene="reflect", payload=payload)
    except Exception as exc:
        typer.echo(f"⚠️ Ошибка отправки события: {exc}")
        raise typer.Exit(code=1)

    if result.get("ok"):
        typer.echo("✅ Событие reflect отправлено.")
    else:
        typer.echo(f"⚠️ Ядро ответило без ok=true: {result}")
        raise typer.Exit(code=1)
