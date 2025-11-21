from __future__ import annotations

from typing import Any, Dict, List

import typer

from ..core.api_client import get_core_status, send_event

# Порядок фаз в одном цикле
PHASES = ["intro", "reflect", "transition", "outro"]


def _detect_last_scene(core: Dict[str, Any]) -> str | None:
    """Определить сцену последнего события из /api/status."""
    events: List[Dict[str, Any]] = core.get("events") or []
    if not events:
        return None
    return events[-1].get("scene")


def _choose_next_scene(last_scene: str | None) -> str:
    """
    Выбрать следующую фазу:

    None / manual / другое → intro
    intro      → reflect
    reflect    → transition
    transition → outro
    outro      → intro (новый цикл)
    """
    if last_scene in PHASES:
        idx = PHASES.index(last_scene)
        if idx + 1 < len(PHASES):
            return PHASES[idx + 1]
        return "intro"
    return "intro"


def _compute_cycle(core: Dict[str, Any], next_scene: str) -> int:
    """
    Прикинуть номер цикла по количеству intro в таймлайне.

    Если следующая сцена intro — считаем, что начинается новый цикл.
    """
    events: List[Dict[str, Any]] = core.get("events") or []
    intro_count = sum(1 for e in events if e.get("scene") == "intro")

    if next_scene == "intro":
        return intro_count + 1

    # Если ещё ни одного intro не было — считаем, что идёт первый цикл
    return intro_count or 1


def next_command(
    text: str = typer.Option(
        "",
        "--text",
        "-t",
        help="Текст события. Если не задан — формируется автоматически.",
    ),
) -> None:
    """
    Автоматический переход к следующей фазе цикла:

    intro → reflect → transition → outro → intro → ...
    """
    try:
        core = get_core_status()
    except Exception as exc:  # сеть / HTTP / JSON
        typer.echo(f"⚠ Ошибка запроса /api/status: {exc}")
        raise typer.Exit(code=1)

    last_scene = _detect_last_scene(core)
    next_scene = _choose_next_scene(last_scene)
    cycle = _compute_cycle(core, next_scene)

    if not text:
        text = f"Цикл {cycle}, фаза {next_scene}"

    payload: Dict[str, Any] = {
        "text": text,
        "cycle": cycle,
        "auto": True,
    }

    try:
        result = send_event(source="cli", scene=next_scene, payload=payload)
    except Exception as exc:
        typer.echo(f"⚠ Ошибка отправки события: {exc}")
        raise typer.Exit(code=1)

    if result.get("ok"):
        typer.echo(f"✅ [{cycle}:{next_scene}] Событие отправлено.")
    else:
        typer.echo(f"⚠ Ядро ответило без ok=true: {result}")
        raise typer.Exit(code=1)
