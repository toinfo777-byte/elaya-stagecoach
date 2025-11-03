# app/entrypoint.py
from __future__ import annotations
import os
import logging

logger = logging.getLogger(__name__)

def _run_web():
    # lazy import, чтобы не тянуть веб-зависимости в воркере
    from app.entrypoint_web import main as web_main
    web_main()

def _run_worker():
    # если у тебя есть воркер — оставляем хуком; иначе просто логи
    try:
        from app.entrypoint_worker import main as worker_main  # type: ignore
    except Exception:  # noqa: BLE001
        logger.warning("MODE=worker, но entrypoint_worker не найден — завершаюсь.")
        return
    worker_main()

def main():
    mode = os.getenv("MODE", "web").lower()
    if mode == "web":
        _run_web()
    elif mode == "worker":
        _run_worker()
    else:
        logger.warning("Неизвестный MODE=%s, запускаю web по умолчанию", mode)
        _run_web()

if __name__ == "__main__":
    main()
