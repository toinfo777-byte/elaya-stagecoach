#!/usr/bin/env python3
from __future__ import annotations

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import textwrap
import requests

# === Настройки окружения ===
TG_TOKEN = os.environ.get("PULSE_TG_TOKEN", "").strip()
TG_CHAT_ID = os.environ.get("PULSE_TG_CHAT_ID", "").strip()

if not TG_TOKEN or not TG_CHAT_ID:
    raise SystemExit("Missing PULSE_TG_TOKEN or PULSE_TG_CHAT_ID")

# === Дата/время под Москву (UTC+3) без сторонних зависимостей ===
now_utc = datetime.utcnow()
now_msk = now_utc + timedelta(hours=3)

date_slug = now_msk.strftime("%Y-%m-%d")
date_human = now_msk.strftime("%d.%m.%Y")

# === Контент Пульса (минимальный, можно менять когда угодно) ===
title = f"✨ Пульс Элайи • {date_human}"
quote = "«Слово дышит, когда его слышат.»"
body_lines = [
    title,
    "",
    quote,
]

tg_text = "\n".join(body_lines)

# === Файлы репозитория: складываем «пульс» в docs/hq/pulse/YYYY/YYYY-MM-DD.md ===
root = Path(".").resolve()
pulse_dir = root / "docs" / "hq" / "pulse" / str(now_msk.year)
pulse_dir.mkdir(parents=True, exist_ok=True)

md_file = pulse_dir / f"{date_slug}.md"
md_file.write_text(
    textwrap.dedent(
        f"""\
        # {title}

        {quote}

        _Автогенерация: GitHub Actions · {now_msk.isoformat(timespec="minutes")} MSK_
        """
    ),
    encoding="utf-8",
)

# обновим легкий индекс (ссылки по годам) — чтобы было что-то видимое в репо
index_dir = root / "docs" / "hq" / "pulse"
index_dir.mkdir(parents=True, exist_ok=True)
index_md = index_dir / "_index.md"

# добавляем/обновляем ссылку на сегодняшний файл в верхней части
rel_link = f"{now_msk.year}/{date_slug}.md"
new_entry = f"- [{date_human}]({rel_link}) — {quote}\n"

if index_md.exists():
    prev = index_md.read_text(encoding="utf-8")
    lines = [ln for ln in prev.splitlines()]
    # вставим новую строку после заголовка, без дублей
    header = "# Пульс Элайи"
    if not lines or not lines[0].startswith(header):
        lines.insert(0, header)
        lines.insert(1, "")
    # удаляем дубликат сегодняшнего
    lines = [ln for ln in lines if f"]({rel_link})" not in ln]
    # вставляем сразу после заголовка
    try:
        insert_at = lines.index("")  # после пустой строки, идущей вслед за заголовком
    except ValueError:
        insert_at = 1
    lines.insert(insert_at + 1, new_entry.rstrip())
    index_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
else:
    index_md.write_text(
        f"# Пульс Элайи\n\n{new_entry}", encoding="utf-8"
    )

# === Публикация в Telegram через «чистый» стейдж-бот ===
# Никаких клавиатур, только sendMessage. Так бот не трогает ваши хендлеры.
api_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
payload = {
    "chat_id": TG_CHAT_ID,
    "text": tg_text,
    "parse_mode": "Markdown",
    "disable_web_page_preview": True,
    "disable_notification": True,  # тихая отправка
}
resp = requests.post(api_url, data=payload, timeout=15)
try:
    data = resp.json()
except Exception:
    data = {"ok": False, "error": resp.text}

if not data.get("ok"):
    raise SystemExit(f"Telegram send failed: {json.dumps(data, ensure_ascii=False)}")
