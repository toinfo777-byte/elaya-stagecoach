# scripts/send_summary.py
import os, json, glob, sys, urllib.parse, urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

def latest_json_path() -> Path:
    cand = sorted(Path("docs/elaya_status").glob("Elaya_Status_*.json"))
    if not cand:
        raise FileNotFoundError("no status json")
    return cand[-1]

def send_tg(token: str, chat_id: str, text: str):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id, "text": text, "parse_mode": "Markdown"
    }).encode()
    with urllib.request.urlopen(url, data=data, timeout=20) as r:
        r.read()

def main():
    token = os.getenv("TG_BOT_TOKEN")
    chat  = os.getenv("TG_STATUS_CHAT_ID")
    if not token or not chat:
        print("TG creds missing", file=sys.stderr)
        return 1

    js = json.loads(latest_json_path().read_text(encoding="utf-8"))
    msk = timezone(timedelta(hours=3))
    today = datetime.now(msk).date().isoformat()

    sentry_ok   = js.get("sentry_ok", False)
    cronitor_ok = js.get("cronitor_ok", False)
    sentry_e = "✅" if sentry_ok else "❗️"
    cronitor_e = "✅" if cronitor_ok else "❗️"

    # очень короткая сводка
    lines = [
        f"🪶 *Daily Status* — {today}",
        f"ENV: {js.get('env','?')} | BUILD: {js.get('build_mark','?')} | SHA: {js.get('git_sha','') or '?'}",
        f"Render: ✅ {js.get('render_status','?')} | Sentry: {sentry_e} | Cronitor: {cronitor_e}",
        f"Uptime: {int(js.get('uptime_sec',0))//3600}h",
        f"{js.get('image','ghcr.io/...')}",
    ]
    text = "\n".join(lines)
    send_tg(token, chat, text)
    return 0

if __name__ == "__main__":
    sys.exit(main())
