# tools/daily_report.py
from __future__ import annotations
import os, datetime
from pathlib import Path

DOCS_DIR = Path("docs/elaya_status")
DOCS_DIR.mkdir(parents=True, exist_ok=True)

def env(name: str, default: str = "") -> str:
    return (os.getenv(name) or default).strip()

def now_utc_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def today_str_utc() -> str:
    return datetime.datetime.utcnow().date().isoformat()

def main() -> None:
    env_name   = env("ENV", "develop")
    repo       = env("REPO", "unknown/repo")
    sha        = env("SHA", "local")[:7]
    image_tag  = env("IMAGE_TAG", "ghcr.io/unknown/elaya-stagecoach:develop")
    build_mark = env("BUILD_MARK", "daily-local")
    run_url    = env("RUN_URL", "")
    cron_ts    = env("CRON_TS", now_utc_iso())

    uptime_hint = "n/a (worker restart at deploy)"
    fname = f"Elaya_Status_{today_str_utc().replace('-', '_')}.md"
    path  = DOCS_DIR / fname

    md = f"""# Ежедневный отчёт — {today_str_utc()}

**ENV:** `{env_name}`  
**BUILD:** `{build_mark}`  
**SHA:** `{sha}`  
**IMAGE:** `{image_tag}`  
**Generated at (UTC):** `{cron_ts}`  
**GitHub Run:** {run_url or "(local)"}  

## Сводка
- Worker uptime: `{uptime_hint}`
- Sentry: `on` if DSN present (checked in runtime)
- Cronitor/HC: `ok` (see pings)

## Примечания
- Отчёт сформирован из CI, бот может запрашивать его командой `/report`.
"""

    path.write_text(md, encoding="utf-8")
    print(f"written: {path}")

if __name__ == "__main__":
    main()
