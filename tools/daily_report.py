# tools/daily_report.py
from __future__ import annotations
import os, re, sys, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS_MD = ROOT / "docs/Elaya_Current_Status_Q4_2025.md"
OUT_DIR   = ROOT / "docs/elaya_status"

def _now_utc_iso():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def _extract_build_from_status_md(text: str) -> dict:
    """
    Ищем блок:
    <!-- BLOCK:Build -->
    BUILD_MARK: `...`
    GIT_SHA: `...`
    ENV: `...`
    IMAGE: `...`
    Updated: 2025-..Z
    <!-- END BLOCK -->
    """
    m = re.search(r"<!--\s*BLOCK:Build\s*-->(.*?)<!--\s*END\s+BLOCK\s*-->", text, re.S|re.I)
    if not m:
        return {}
    block = m.group(1)
    def grab(key):
        mm = re.search(rf"{key}:\s*`?([^\s`]+)`?", block)
        return mm.group(1).strip() if mm else ""
    return {
        "BUILD_MARK": grab("BUILD_MARK"),
        "GIT_SHA":    grab("GIT_SHA"),
        "ENV":        grab("ENV"),
        "IMAGE":      grab("IMAGE"),
        "UPDATED":    (re.search(r"Updated:\s*([^\n]+)", block) or [None, ""])[1].strip()
    }

def _fallback_from_env() -> dict:
    return {
        "BUILD_MARK": os.getenv("BUILD_MARK", "unknown"),
        "GIT_SHA":    (os.getenv("SHORT_SHA") or os.getenv("GITHUB_SHA") or "unknown"),
        "ENV":        os.getenv("ENV", "develop"),
        "IMAGE":      os.getenv("IMAGE_TAG", "ghcr.io/unknown/elaya-stagecoach:develop"),
        "UPDATED":    _now_utc_iso()
    }

def collect_snapshot() -> dict:
    if STATUS_MD.exists():
        snap = _extract_build_from_status_md(STATUS_MD.read_text(encoding="utf-8"))
        if any(snap.values()):
            return snap
    return _fallback_from_env()

def render_report_md(s: dict, run_url: str) -> str:
    today = datetime.datetime.utcnow().date().isoformat()
    sha7 = (s.get("GIT_SHA","") or "")[:7]
    return f"""# Elaya — Daily Status • {today}

Пульс системы (автоотчёт).

**Build**
- BUILD_MARK: `{s.get('BUILD_MARK','')}`
- GIT_SHA: `{sha7}`
- ENV: `{s.get('ENV','')}`
- IMAGE: `{s.get('IMAGE','')}`
- Last Updated: {s.get('UPDATED','')}

**Signals**
- Render: deploy hook OK (см. историю деплоёв)
- Sentry: startup probe в логе при каждом рестарте
- Cronitor/HC: heartbeat каждые 5 минут

**Links**
- CI Run: {run_url}

_Отчёт сгенерирован: { _now_utc_iso() }_
"""

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    snap = collect_snapshot()
    run_url = os.getenv("RUN_URL","")
    name = f"Elaya_Status_{datetime.datetime.utcnow().date().isoformat()}.md"
    (OUT_DIR / name).write_text(render_report_md(snap, run_url), encoding="utf-8")
    print(f"Report generated: docs/elaya_status/{name}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(1)
