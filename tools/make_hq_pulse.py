#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HQ Pulse generator:
- читает STATUS_JSON_URL (если задан) или собирает базовый статус из репо
- пишет docs/hq/pulse/HQ_Pulse_YYYY-MM-DD.md
- обновляет README.md между маркерами <!-- HQ_PULSE:START --> ... <!-- HQ_PULSE:END -->
env:
  STATUS_JSON_URL (optional) — URL до /status_json
  PULSE_TZ (optional) — таймзона для дат (default: Europe/Moscow)
  GITHUB_SERVER_URL, GITHUB_REPOSITORY (из GitHub Actions)
  PULSE_BRANCH (optional) — ветка, где живёт пулс (default: develop)
"""
from __future__ import annotations
import os, re, json, subprocess, urllib.request, urllib.error, datetime
from pathlib import Path

def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()

def read_status_json(url: str) -> dict | None:
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            if r.status == 200:
                return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None
    return None

def import_build_mark() -> str | None:
    try:
        import importlib.util, sys
        # позволим импортировать локальный пакет app/
        root = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(root))
        spec = importlib.util.spec_from_file_location("app.build", root / "app" / "build.py")
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)  # type: ignore
            return getattr(mod, "BUILD_MARK", None)
    except Exception:
        return None
    return None

def today_in_tz(tz_name: str) -> datetime.date:
    try:
        from zoneinfo import ZoneInfo  # py>=3.9
        now = datetime.datetime.now(ZoneInfo(tz_name))
    except Exception:
        now = datetime.datetime.utcnow()
    return now.date()

def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    docs_dir = repo_root / "docs" / "hq" / "pulse"
    docs_dir.mkdir(parents=True, exist_ok=True)

    tz = os.getenv("PULSE_TZ", "Europe/Moscow")
    date = today_in_tz(tz)
    date_str = date.isoformat()
    pretty_date = date.strftime("%-d %B %Y") if hasattr(date, "strftime") else date_str

    # 1) пробуем /status_json
    status = {}
    url = os.getenv("STATUS_JSON_URL", "").strip()
    if url:
        status = read_status_json(url) or {}

    # 2) резервные источники
    try:
        short_sha = run(["git", "rev-parse", "--short", "HEAD"])
    except Exception:
        short_sha = "unknown"

    build_mark = import_build_mark() or "—"

    # собираем поля
    status_emoji = status.get("status_emoji") or "🌞"
    status_word = status.get("status_word") or "Stable"
    focus = status.get("focus") or "Система в ритме дыхания"
    note = status.get("note") or "Web и Bot синхронны; пульс ровный."
    uptime = status.get("uptime") or "—"
    build = status.get("build") or short_sha

    # Файлик пульса
    md_name = f"HQ_Pulse_{date_str}.md"
    md_path = docs_dir / md_name

    # Тихая метафора месяца — можно задать через STATUS_JSON, иначе — дефолт
    month_quote = status.get("quote") or "«Ноябрь — дыхание изнутри.»"

    content = f"""# 💠 HQ PULSE — {pretty_date}
**Status:** {status_emoji} {status_word}  
**Build:** {build} · uptime {uptime}  
**Focus:** {focus}  
**Note:** {note}  
🕯 {month_quote}
"""
    md_path.write_text(content, encoding="utf-8")

    # Обновляем README блок
    readme = repo_root / "README.md"
    start = "<!-- HQ_PULSE:START -->"
    end = "<!-- HQ_PULSE:END -->"
    link_branch = os.getenv("PULSE_BRANCH", "develop")
    server = os.getenv("GITHUB_SERVER_URL", "https://github.com")
    repo = os.getenv("GITHUB_REPOSITORY", "owner/repo")
    pulse_url = f"{server}/{repo}/blob/{link_branch}/docs/hq/pulse/{md_name}"

    last_block = f"🪶 **Last Pulse** → [{md_name}]({pulse_url})"

    if readme.exists():
        txt = readme.read_text(encoding="utf-8")
        if start in txt and end in txt:
            new = re.sub(
                rf"{re.escape(start)}.*?{re.escape(end)}",
                f"{start}\n{last_block}\n{end}",
                txt,
                flags=re.DOTALL,
            )
        else:
            # если маркеров нет — добавим в конец
            new = txt.rstrip() + f"\n\n{start}\n{last_block}\n{end}\n"
        readme.write_text(new, encoding="utf-8")
    else:
        readme.write_text(f"# Elaya StageCoach\n\n{start}\n{last_block}\n{end}\n", encoding="utf-8")

    print(f"Pulse written: {md_path}")

if __name__ == "__main__":
    main()
