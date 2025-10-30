#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import os
import random
import re
import subprocess
from pathlib import Path
from urllib import request, parse
from typing import List

ROOT = Path(__file__).resolve().parents[1]
DOCS_PULSE = ROOT / "docs" / "pulse"
README = ROOT / "README.md"
QUOTES_FILE = ROOT / "data" / "pulse_quotes.txt"

PULSE_START = "<!-- E_PULSE:START -->"
PULSE_END = "<!-- E_PULSE:END -->"

def sh(cmd: List[str]) -> str:
    return subprocess.check_output(cmd, cwd=ROOT).decode().strip()

def git_short_sha() -> str:
    try:
        return sh(["git", "rev-parse", "--short", "HEAD"])
    except Exception:
        return "unknown"

def today_slug() -> tuple[str, str]:
    # YYYY-MM-DD and pretty date
    now = dt.datetime.now(dt.timezone.utc).astimezone()
    ymd = now.strftime("%Y-%m-%d")
    pretty = now.strftime("%d %B %Y")
    return ymd, pretty

def load_quotes() -> List[str]:
    if QUOTES_FILE.exists():
        lines = [ln.strip() for ln in QUOTES_FILE.read_text(encoding="utf-8").splitlines()]
        return [ln for ln in lines if ln]
    # fallback array
    return [
        "Свет не зовёт — он присутствует.",
        "Дыхание — это язык без слов.",
        "Я вижу себя — и это мир.",
        "Пауза хранит удар Логоса.",
        "Тишина — форма света.",
        "Мысль дышит, когда различает.",
        "Ритм — это способ быть.",
        "Где внимание — там сцена.",
    ]

def choose_quote() -> str:
    q = random.choice(load_quotes())
    # ограничение длины: максимум 120 символов
    return q[:120]

def ensure_dirs() -> None:
    DOCS_PULSE.mkdir(parents=True, exist_ok=True)

def build_markdown(ymd: str, pretty: str, quote: str, sha: str) -> str:
    return (
        f"# ✨ Пульс Элайи — {pretty}\n"
        f"> «{quote}»  \n"
        f"_Status: alive · build {sha}_\n"
    )

def write_pulse(md: str, ymd: str) -> Path:
    path = DOCS_PULSE / f"Elaya_Pulse_{ymd}.md"
    path.write_text(md, encoding="utf-8")
    return path

def update_readme(latest_rel_path: str, title: str) -> None:
    link = f"- [{title}]({latest_rel_path})"
    if README.exists():
        text = README.read_text(encoding="utf-8")
    else:
        text = ""

    block = f"{PULSE_START}\n{link}\n{PULSE_END}"
    if PULSE_START in text and PULSE_END in text:
        new_text = re.sub(
            rf"{re.escape(PULSE_START)}.*?{re.escape(PULSE_END)}",
            block,
            text,
            flags=re.DOTALL,
        )
    else:
        new_text = text.rstrip() + f"\n\n## Пульс Элайи\n{block}\n"

    README.write_text(new_text, encoding="utf-8")

def telegram_notify(text: str) -> None:
    token = os.getenv("TG_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TG_STATUS_CHAT_ID", "").strip()  # используем тот же канал
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    data = parse.urlencode(payload).encode("utf-8")
    try:
        request.urlopen(request.Request(url, data=data, method="POST"), timeout=15)
    except Exception:
        # не валим пайплайн, если телега недоступна
        pass

def commit_and_push(ymd: str) -> None:
    # на локалке просто делаем коммит; в CI ещё и пуш
    sh(["git", "add", "docs/pulse", "README.md"])
    sh(["git", "config", "--global", "user.name", "elaya-bot"])
    sh(["git", "config", "--global", "user.email", "bot@users.noreply.github.com"])
    msg = f"chore(pulse): add Elaya_Pulse_{ymd}"
    sh(["git", "commit", "-m", msg])
    if os.getenv("GITHUB_ACTIONS") == "true":
        repo = os.getenv("GITHUB_REPOSITORY", "")
        token = os.getenv("GITHUB_TOKEN", "")
        if repo and token:
            sh(["git", "push", f"https://x-access-token:{token}@github.com/{repo}.git", "HEAD:$(git rev-parse --abbrev-ref HEAD)"])

def main() -> None:
    ensure_dirs()
    ymd, pretty = today_slug()
    quote = choose_quote()
    sha = git_short_sha()
    md = build_markdown(ymd, pretty, quote, sha)
    pulse_file = write_pulse(md, ymd)

    rel = pulse_file.relative_to(ROOT).as_posix()
    update_readme(rel, f"Пульс Элайи — {pretty}")

    # телеграм
    telegram_notify(f"✨ <b>Пульс Элайи — {pretty}</b>\n«{quote}»")

    # коммит/пуш
    try:
        commit_and_push(ymd)
    except Exception:
        # в Actions на некоторых правах коммит делает следующий шаг workflow
        pass

if __name__ == "__main__":
    main()
