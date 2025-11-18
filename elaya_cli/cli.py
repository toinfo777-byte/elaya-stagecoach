#!/usr/bin/env python3
# cli.py — минимальный CLI Элайя-Агента v0.2

import datetime
import os
import sys

from elaya.core import get_status

# -----------------------------
# Команды
# -----------------------------

def show_help():
    print("""
Elaya Agent · v0.2

Доступные команды:

  elaya help       — показать помощь
  elaya status     — статус локального слоя
  elaya project    — информация о проекте (папки, время, структура)

""")


def show_status() -> None:
    data = get_status()
    print("Elaya Status:")
    print(f"  Status : {data['status']}")
    print(f"  Time   : {data['time']}")
    print(f"  Folder : {data['cwd']}")





def show_project():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    docs = os.path.join(root, "docs")
    app = os.path.join(root, "app")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("Elaya Project Info:")
    print(f"  Time : {now}")
    print(f"  Root : {root}")
    print(f"  Docs : {docs}")
    print(f"  App  : {app}")


# -----------------------------
# Основной вход
# -----------------------------

def main():
    if len(sys.argv) < 2:
        show_help()
        return

    cmd = sys.argv[1]

    if cmd == "help":
        show_help()
    elif cmd == "status":
        show_status()
    elif cmd == "project":
        show_project()
    else:
        print(f"Неизвестная команда: {cmd}")
        show_help()


if __name__ == "__main__":
    main()

def main():
    import sys

    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1]

    if command == "help":
        show_help()
    elif command == "status":
        show_status()
    elif command == "project":
        show_project()
    else:
        print(f"Неизвестная команда: {command}")
        show_help()


if __name__ == "__main__":
    main()
