from .commands.event_cmd import event

app = typer.Typer(help="Локальный CLI-агент Элайи")

app.command()(status)
app.command()(diag)
app.command()(project)
app.command()(sync)
app.command()(event)  # ← эта строка
