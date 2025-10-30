#!/usr/bin/env python3
from __future__ import annotations
import datetime as dt
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR  = REPO_ROOT / "docs" / "hq" / "pulse"
README    = REPO_ROOT / "README.md"

today = dt.date.today()
y = f"{today:%Y}"
m = f"{today:%m}"
d = f"{today:%Y-%m-%d}"

target_dir = DOCS_DIR / y / m
target_dir.mkdir(parents=True, exist_ok=True)
target_md  = target_dir / f"{d}.md"

if not target_md.exists():
    target_md.write_text(
        f"# Пульс Элайи — {d}\n\n"
        f"_Автогенерация snapshot’а._\n\n"
        f"- Дата: **{d}**\n"
        f"- Источник: GitHub Actions\n"
    , encoding="utf-8")

# Обновим в README ссылку на последний пульс
rel_link = f"docs/hq/pulse/{y}/{m}/{d}.md"
badge = f"[Пульс · {d}]({rel_link})"
if README.exists():
    txt = README.read_text(encoding="utf-8")
    marker = "<!-- ELAYA_PULSE_LINK -->"
    if marker in txt:
        pre, post = txt.split(marker, 1)
        new = pre + marker + "\n\n" + badge + "\n"
        if post.startswith("\n"):
            new += post  # сохраняем остальное
        README.write_text(new, encoding="utf-8")
    else:
        README.write_text(txt + f"\n\n{marker}\n\n{badge}\n", encoding="utf-8")
