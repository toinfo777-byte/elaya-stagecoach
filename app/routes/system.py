# app/routes/system.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import os

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from app.core.cycle_state import CycleState

router = APIRouter(prefix="/api", tags=["api"])

# --- защита для мутаций (по желанию через GUARD_KEY) ---


GUARD_KEY = os.getenv("GUARD_KEY", "").strip()


def _check_guard(x_guard_key: Optional[str]) -> None:
    """
    Простая защита для мутирующих запросов.

    Если GUARD_KEY не задан в окружении — защита выключена.
    Если задан — все запросы с изменением состояния должны
    присылать заголовок X-Guard-Key.
    """
    if not GUARD_KEY:
        return
    if (x_guard_key or "").strip() != GUARD_KEY:
        raise HTTPException(status_code=401, detail="invalid guard key")


# --- внутренняя модель хранилища ядра ---


class StateStore:
    """
    Минимальное in-memory ядро состояния Элайи.

    Здесь живут:
    - номер цикла
    - счётчики фаз
    - список событий таймлайна
    - последний текст reflection
    """

    def __init__(self) -> None:
        self.cycle: int = 0
        self.last_update: str = "-"
        self.intro: int = 0
        self.reflect: int = 0
        self.transition: int = 0
        self.events: List[Dict[str, Any]] = []
        self.reflection: Dict[str, Any] = {"text": "", "updated_at": "-"}

    # --- основная логика ядра ---

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def add_event(self, *, source: str, scene: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Добавляет событие в таймлайн и обновляет счётчики.

        Логика:
        - если сцена intro:
            * увеличиваем счётчик intro
            * если предыдущая сцена была transition/next/нет событий — увеличиваем номер цикла
        - reflect / transition — только счётчики
        - next — просто событие (служебная отметка между циклами)
        """
        ts = self._now()
        scene = (scene or "").strip() or "manual"

        prev_scene: Optional[str] = self.events[-1]["scene"] if self.events else None

        if scene == "intro":
            self.intro += 1
            if prev_scene in (None, "transition", "next"):
                self.cycle += 1
        elif scene == "reflect":
            self.reflect += 1
        elif scene == "transition":
            self.transition += 1

        event = {
            "ts": ts,
            "source": source,
            "scene": scene,
            "payload": payload or {},
        }
        self.events.append(event)
        self.last_update = ts
        return event

    def set_reflection(self, text: str) -> None:
        ts = self._now()
        self.reflection = {"text": text, "updated_at": ts}
        self.last_update = ts

    def to_dict(self) -> Dict[str, Any]:
        """
        Снимок состояния для /api/status.
        """
        return {
            "cycle": self.cycle,
            "last_update": self.last_update,
            "intro": self.intro,
            "reflect": self.reflect,
            "transition": self.transition,
            "events": list(self.events),
            "reflection": dict(self.reflection),
        }


# Глобальное ядро для текущего процесса.
state = StateStore()

# --- модели запросов / ответов ---


class EventIn(BaseModel):
    source: str
    scene: str
    payload: Dict[str, Any] = {}


class ReflectionIn(BaseModel):
    text: str


# --- эндпоинты ядра ---


@router.get("/status")
def get_status() -> Dict[str, Any]:
    """
    Текущий статус ядра Элайи.
    Используется CLI-командой `elaya3 status`.
    """
    core = state.to_dict()
    return {"ok": True, "core": core}


@router.get("/timeline")
def get_timeline() -> Dict[str, Any]:
    """
    Сырой таймлайн для внутренних клиентов (UI, отладка).
    """
    core = state.to_dict()
    return {"ok": True, "events": core.get("events", [])}


@router.post("/event")
def post_event(
    event_in: EventIn,
    x_guard_key: Optional[str] = Header(None, alias="X-Guard-Key"),
) -> Dict[str, Any]:
    """
    Приём события от CLI / других агентов.
    """
    _check_guard(x_guard_key)

    event = state.add_event(
        source=event_in.source,
        scene=event_in.scene,
        payload=event_in.payload,
    )
    return {"ok": True, "event": event}


@router.post("/reflection")
def post_reflection(
    reflection_in: ReflectionIn,
    x_guard_key: Optional[str] = Header(None, alias="X-Guard-Key"),
) -> Dict[str, Any]:
    """
    Сохранение короткого отражения / заметки в ядре.
    """
    _check_guard(x_guard_key)
    state.set_reflection(reflection_in.text)
    return {"ok": True, "reflection": state.reflection}


@router.get("/cycle/state")
def get_cycle_state() -> Dict[str, Any]:
    """
    Высокоуровневое состояние цикла Элайи.

    Используется для:
    - CLI-команд вроде `elaya3 cycle`
    - UI-панели /timeline (заголовок)
    - тренер-бота (понимать, где мы в цикле)
    """
    core = state.to_dict()
    cycle_state = CycleState.from_core(core).to_dict()
    return {"ok": True, "cycle": cycle_state}


@router.post("/cycle/next")
def post_cycle_next(
    x_guard_key: Optional[str] = Header(None, alias="X-Guard-Key"),
) -> Dict[str, Any]:
    """
    Автоматический шаг цикла.

    Берём текущее состояние, вычисляем следующую фазу
    и записываем событие от источника "cycle_engine".
    """
    _check_guard(x_guard_key)

    # 1) читаем текущее состояние
    core_before = state.to_dict()
    cycle_state = CycleState.from_core(core_before)

    phase = (cycle_state.phase or "idle").strip() or "idle"

    # 2) определяем следующую сцену
    if phase == "intro":
        next_scene = "reflect"
    elif phase == "reflect":
        next_scene = "transition"
    elif phase == "transition":
        next_scene = "next"
    else:
        # idle, next, неизвестное → стартуем / перезапускаем цикл
        next_scene = "intro"

    # 3) записываем событие в ядро
    event = state.add_event(
        source="cycle_engine",
        scene=next_scene,
        payload={"prev_phase": phase},
    )

    # 4) берём обновлённое состояние
    core_after = state.to_dict()
    new_cycle_state = CycleState.from_core(core_after).to_dict()

    return {
        "ok": True,
        "cycle": new_cycle_state,
        "event": event,
    }
