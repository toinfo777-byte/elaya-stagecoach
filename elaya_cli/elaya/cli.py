from __future__ import annotations

from . import app


def main() -> None:
    """
    Точка входа для elaya3 (указывать в entry_points).
    """
    app()


# Возможен прямой запуск: python -m elaya_cli.elaya.cli
if __name__ == "__main__":
    main()
