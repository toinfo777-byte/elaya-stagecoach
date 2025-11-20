from __future__ import annotations

from typing import Any, Dict

import typer

from ..core.api_client import send_event


def event(
    text: str = typer.Argument(..., help="Текст события для таймлайна"),
    scene: str = typer.Option(
        "manual",
        "--scene",
        "-s",
        help="Сцена / контекст события (по умолчанию 'manual')",
    ),
) -> None:
    """
    Отправить событие в таймлайн Элайи из CLI.
    """
    payload: Dict[str, Any] = {"text": text}

    try:
        result = send_event(source="cli", scene=scene, payload=payload)
    except Exception as exc:  # сеть, HTTP-ошибки и т.п.
        typer.echo(f"⚠️  Ошибка отправки события: {exc}")
        raise typer.Exit(code=1)

    if result.get("ok"):
        typer.echo("✅ Событие отправлено.")
    else:
        typer.echo(f"⚠️  Ядро ответило без ok=true: {result}")
        raise typer.Exit(code=1)
