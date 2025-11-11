#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HQ Pulse generator:
- читает STATUS_JSON_URL (если задан) или собирает базовый статус из репо
- дополнительно, если задан UI_STATS_URL или ELAYA_BASE_URL, подтягивает /ui/stats.json
- пишет docs/hq/pulse/HQ_Pulse_YYYY-MM-DD.md
- обновляет README.md между маркерами <!-- HQ_PULSE:START --> ... <!-- HQ_PULSE:END -->

env:
  STATUS_JSON_URL (optional) — URL до /status_json
  UI_STATS_URL    (optional) — прямой URL до /ui/stats.json
  ELAYA_BASE_URL  (optional) — базовый URL, из него будет собран {ELAYA_BASE_URL}/ui/stats.json
  PULSE_TZ        (optional) — таймзона для дат (default: Europe/Moscow)
  GITHUB_SERVER_URL, GITHUB_REPOSITORY (из GitHub Actions)
  PULSE_BRANCH    (optional) — ветка, где живёт пулс (default: develop)
"""
from __future__ import annotations
import os, re, json, subprocess, urllib.request, urllib.error, datetime
from pathlib import Path


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()


def read_json(url: str) -> dict | None:
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            if getattr(r, "status", 200) == 200:
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


def render_scene_stats(stats: dict | None) -> str:
    if not stats:
        return ""
    counts = stats.get("counts") or stats.get("scene_counts") or {}
    intro = counts.get("intro", 0)
    refl = counts.get("reflect", 0)
    trans = counts.get("transition", 0)
    users = stats.get("users", 0)
    lr_text = (stats.get("last_reflection") or {}).get("text") or stats.get("last_reflect") or "—"
    lr_at = (stats.get("last_reflection") or {}).get("at") or stats.get("last_update") or stats.get("last_updated") or "—"
    return (
        f"\n**Scene stats**: users={users}, intro={intro}, reflect={refl}, transition={trans}\n"
        f"**Last reflection**: “{lr_text}” *(at {lr_at})*\n"
    )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    docs_dir = repo_root / "docs" / "hq" / "pulse"
    docs_dir.mkdir(parents=True, exist_ok=True)

    tz = os.getenv("PULSE_TZ", "Europe/Moscow")
    date = today_in_tz(tz)
    date_str = date.isoformat()
    # %-d красиво работает в *nix. На Windows упадёт — тогда останется ISO.
    try:
        pretty_date = date.strftime("%-d %B %Y")
    except Exception:
        pretty_date = date_str

    # 1) статус из внешнего JSON (если есть)
    status: dict = {}
    status_url = os.getenv("STATUS_JSON_URL", "").strip()
    if status_url:
        status = read_json(status_url) or {}

    # 2) резерв: git и build mark
    try:
        short_sha = run(["git", "rev-parse", "--short", "HEAD"])
    except Exception:
        short_sha = "unknown"
    build_mark = import_build_mark() or "—"

    # 3) scene stats (ui)
    ui_stats: dict | None = None
    ui_stats_url = os.getenv("UI_STATS_URL", "").strip()
    if not ui_stats_url:
        base = os.getenv("ELAYA_BASE_URL", "").rstrip("/")
        if base:
            ui_stats_url = f"{base}/ui/stats.json"
    if ui_stats_url:
        ui_stats = read_json(ui_stats_url)

    # собираем поля
    status_emoji = status.get("status_emoji") or "🌞"
    status_word  = status.get("status_word")  or "Stable"
    focus        = status.get("focus")        or "Система в ритме дыхания"
    note         = status.get("note")         or "Web и Bot синхронны; пульс ровный."
    uptime       = status.get("uptime")       or "—"
    build        = status.get("build")        or short_sha or build_mark

    # файл пульса
    md_name = f"HQ_Pulse_{date_str}.md"
    md_path = docs_dir / md_name

    # Тихая метафора месяца
    month_quote = status.get("quote") or "«Ноябрь — дыхание изнутри.»"

    content = (
        f"# 💠 HQ PULSE — {pretty_date}\n"
        f"**Status:** {status_emoji} {status_word}  \n"
        f"**Build:** {build} · uptime {uptime}  \n"
        f"**Focus:** {focus}  \n"
        f"**Note:** {note}  \n"
        f"🕯 {month_quote}\n"
    )

    # врезка сцен
    scene_block = render_scene_stats(ui_stats)
    if scene_block:
        content += scene_block

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
            new = txt.rstrip() + f"\n\n{start}\n{last_block}\n{end}\n"
        readme.write_text(new, encoding="utf-8")
    else:
        readme.write_text(
            f"# Elaya StageCoach\n\n{start}\n{last_block}\n{end}\n",
            encoding="utf-8",
        )

    print(f"Pulse written: {md_path}")


if __name__ == "__main__":
    main()
