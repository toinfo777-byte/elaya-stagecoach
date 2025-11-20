import typer

from ..core.config import APP_NAME, APP_VERSION


def run() -> None:
    typer.echo(f"{APP_NAME} v{APP_VERSION}")
    typer.echo()
    typer.echo("Доступные команды:")
    typer.echo("  elaya help    - показать это сообщение")
    typer.echo("  elaya status  - состояние агента и проекта")
    typer.echo("  elaya project - информация о структуре проекта")
    typer.echo("  elaya diag    - лёгкая диагностика окружения")
    typer.echo("  elaya sync    - синхронизация с web-core (если настроен)")
    typer.echo()
    typer.echo("Подсказка: elaya --help также покажет встроенную помощь Typer.")
