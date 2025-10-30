# tools/tg_notify.py
from __future__ import annotations
import os
import json
import urllib.request
import urllib.parse


def _env(name: str) -> str | None:
    v = os.getenv(name)
    return v.strip() if v else None


def main() -> None:
    # 1) PULSE_* приоритет
    token = _env("PULSE_TG_TOKEN") or _env("TG_BOT_TOKEN")
    chat_id = _env("PULSE_TG_CHAT_ID") or _env("TG_STATUS_CHAT_ID")
    text = _env("PULSE_TEXT") or "Пульс Элайи"

    # Если нет токенов — выходим без ошибки (не ломаем CI)
    if not token or not chat_id:
        print("tg_notify: no TOKEN/CHAT_ID provided — skip sending")
        return

    api_url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(api_url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=20) as r:
        body = r.read().decode("utf-8")
        try:
            resp = json.loads(body)
        except Exception:
            resp = {"raw": body}
        print("tg_notify: sent", resp)


if __name__ == "__main__":
    main()
