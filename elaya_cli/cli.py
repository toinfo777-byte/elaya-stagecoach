#!/usr/bin/env python3
# cli.py — минимальный CLI Элайя-Агента v0.1

import sys
from elaya.core import get_status


def show_help():
    print("""
Elaya Agent · v0.1

Доступные команды:

  elaya help      — показать помощь
  elaya status    — статус локального слоя
""")


def show_status():
    data = get_status()
    print("Elaya Status:")
    print(f"  Status : {data['status']}")
    print(f"  Time   : {data['time']}")
    print(f"  Folder : {data['cwd']}")


def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "help":
        show_help()
    elif cmd == "status":
        show_status()
    else:
        print(f"Неизвестная команда: {cmd}")
        show_help()


if __name__ == "__main__":
    main()
