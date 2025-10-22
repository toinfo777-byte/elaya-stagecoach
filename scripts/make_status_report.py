# scripts/make_status_report.py
import argparse, json, os, sys, textwrap, urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

def human_uptime(sec: int) -> str:
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    if s and not parts: parts.append(f"{s}s")
    return " ".join(parts) or "0s"

def fetch_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="STATUS_URL (/status_json)")
    args = ap.parse_args()

    data = fetch_json(args.url)

    # дата отчёта — по Москве
    msk = timezone(timedelta(hours=3))
    today = datetime.now(msk).date()
    date_str = today.isoformat()

    sentry_emoji   = "✅" if data.get("sentry_ok") else "❗️"
    cronitor_emoji = "✅" if data.get("cronitor_ok") else "❗️"
    uptime = human_uptime(int(data.get("uptime_sec", 0)))

    md = textwrap.dedent(f"""\
    # 🪶 Daily Status — {date_str}

    **ENV:** {data.get("env","?")}  
    **BUILD:** {data.get("build_mark","?")}  
    **GIT SHA:** {data.get("git_sha","") or "?"}  
    **IMAGE:** {data.get("image","?")}  

    **Render:** {data.get("render_status","?")}  
    **Sentry:** {sentry_emoji}  
    **Cronitor:** {cronitor_emoji} (last: {data.get("cronitor_last_ping_iso","") or "—"})

    **Uptime:** {uptime}

    _Generated automatically by GitHub Actions._
    """)

    outdir = Path("docs/elaya_status")
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / f"Elaya_Status_{today.strftime('%Y%m%d')}.md"
    if outpath.exists():
        # идемпотентность: переписываем тем же контентом, чтобы commit мог быть "No changes"
        old = outpath.read_text(encoding="utf-8")
        if old.strip() == md.strip():
            print("No content changes")
        else:
            outpath.write_text(md, encoding="utf-8")
    else:
        outpath.write_text(md, encoding="utf-8")

    # положим рядом json — пригодится для сводки
    (outdir / f"Elaya_Status_{today.strftime('%Y%m%d')}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

if __name__ == "__main__":
    sys.exit(main())
