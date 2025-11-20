from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from elaya.core import get_status, get_project_info, get_diag_info


# --- утилиты вывода ---

def _print_header(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def _fmt_time(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _print_usage() -> None:
    print("""
Elaya Agent · v0.2

Доступные команды:

  elaya help      — показать помощь
  elaya status    — статус локального слоя
  elaya project   — информация о проекте (папки, время, структура)
  elaya diag      — диагностика окружения (пути, Python, venv)
""".strip())


# --- команды ---


def cmd_help(args: list[str]) -> int:
    _print_usage()
    return 0


def cmd_status(args: list[str]) -> int:
    info = get_status()
    _print_header("Elaya Status")

    print(f"Status : {info.status}")
    print(f"Time   : {_fmt_time(info.time)}")
    print(f"Folder : {info.folder}")

    return 0


def cmd_project(args: list[str]) -> int:
    info = get_project_info()
    _print_header("Elaya Project Info")

    print(f"Time : {_fmt_time(info.time)}")
    print(f"Root : {info.root}")
    print(f"Docs : {info.docs}")
    print(f"App  : {info.app}")

    return 0


def cmd_diag(args: list[str]) -> int:
    info = get_diag_info()
    _print_header("Elaya Diagnostics")

    print(f"Python  : {info.python}")
    print(f"Venv    : {info.venv}")
    print(f"Project : {info.project_root}")

    if info.warnings:
        print()
        print("Warnings:")
        for w in info.warnings:
            print(f"- {w}")

    return 0


# --- точка входа ---


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        # Без аргументов показываем help
        _print_usage()
        return 0

    cmd, *rest = argv

    if cmd in ("help", "-h", "--help"):
        return cmd_help(rest)
    if cmd == "status":
        return cmd_status(rest)
    if cmd == "project":
        return cmd_project(rest)
    if cmd == "diag":
        return cmd_diag(rest)

    print(f"Неизвестная команда: {cmd}")
    _print_usage()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
