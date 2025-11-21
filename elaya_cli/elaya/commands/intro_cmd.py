from __future__ import annotations

from typing import Any, Dict

import typer

from ..core.api_client import send_event


def intro(
    text: str = typer.Argument(..., help="Текст события для фазы 'intro'"),
) -> None:
    """
    Отправить событие в фазу intro (вход в цикл).
    """

    payload: Dict[str, Any] = {"text": text}

    try:
        result = send_event(source="cli", scene="intro", payload=payload)
    except Exception as exc:
        typer.echo(f"⚠️ Ошибка отправки события: {exc}")
        raise typer.Exit(code=1)

    if result.get("ok"):
        typer.echo("✅ Событие intro отправлено.")
    else:
        typer.echo(f"⚠️ Ядро ответило без ok=true: {result}")
        raise typer.Exit(code=1)
