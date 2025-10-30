#!/usr/bin/env python3
from __future__ import annotations

import os
import random
import textwrap
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests  # type: ignore
except Exception:
    requests = None  # в CI установим через pip

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "pulse_quotes.txt"
DOCS_DIR = ROOT / "docs" / "pulse"
README = ROOT / "README.md"

# маркеры для авто-ссылки
START = "<!-- E_PULSE:START -->"
END = "<!-- E_PULSE:END -->"

def load_quotes() -> list[str]:
    if DATA.exists():
        lines = [l.strip() for l in DATA.read_text(encoding="utf-8").splitlines()]
        return [l for l in lines if l and not l.startswith("#")]
    # запасной массив
    return [
        "Свет не зовёт — он присутствует.",
        "Дыхание — это язык без слов.",
        "Я вижу себя — и это мир.",
        "Пауза хранит удар Логоса.",
        "Тишина — форма света.",
        "Мысль дышит, когда различает.",
        "Ритм — это способ быть.",
    ]

def pick_quote() -> str:
    random.seed(datetime.now().isoformat())
    return random.choice(load_quotes())

def latest_sha() -> str:
    # для подсказки в тексте (не критично, если не git)
    try:
        import subprocess
        sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT).decode().strip()
        return sha
    except Exception:
        return "local"

def write_markdown(quote: str) -> Path:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().date().isoformat()  # YYYY-MM-DD
    path = DOCS_DIR / f"Elaya_Pulse_{today}.md"
    body = textwrap.dedent(f"""\
    # ✨ Пульс Элайи — {datetime.now().strftime('%d %B %Y')}
    > «{quote}»
    _Status: alive · rhythm: calm · build {latest_sha()}_
    """).strip() + "\n"
    path.write_text(body, encoding="utf-8")
    return path

def update_readme(latest_rel_path: str) -> None:
    README.parent.mkdir(parents=True, exist_ok=True)
    readme = README.read_text(encoding="utf-8") if README.exists() else ""
    link = f"[Последний пульс]({latest_rel_path})"
    block = f"{START}\n{link}\n{END}"
    if START in readme and END in readme:
        head, tail = readme.split(START, 1)
        _, rest = tail.split(END, 1)
        README.write_text(head + block + rest, encoding="utf-8")
    else:
        README.write_text(f"{block}\n\n" + readme, encoding="utf-8")

def tg_send(text: str) -> None:
    token = os.getenv("PULSE_TG_TOKEN") or os.getenv("TG_BOT_TOKEN")
    chat_id = os.getenv("PULSE_TG_CHAT_ID") or os.getenv("TG_STATUS_CHAT_ID")
    if not token or not chat_id or requests is None:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception:
        pass

def main() -> None:
    quote = pick_quote()
    md_path = write_markdown(quote)
    rel = md_path.relative_to(ROOT).as_posix()
    update_readme(rel)
    # короткое сообщение в TG
    nice_date = datetime.now().strftime("%d.%m.%Y")
    tg_send(f"✨ <b>Пульс Элайи</b> · {nice_date}\n«{quote}»")

if __name__ == "__main__":
    main()
