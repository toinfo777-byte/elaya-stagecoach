from __future__ import annotations
import os, pathlib, datetime as dt, json
import requests

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]

def msk_now() -> dt.datetime:
    # раннер в UTC — даём сдвиг +3
    return dt.datetime.utcnow() + dt.timedelta(hours=3)

def ensure_dir(p: pathlib.Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def send_tg(text: str) -> None:
    token = os.getenv("PULSE_TG_TOKEN") or os.getenv("TG_BOT_TOKEN")
    chat_id = os.getenv("PULSE_TG_CHAT_ID") or os.getenv("TG_STATUS_CHAT_ID")
    if not token or not chat_id:
        print("TG env missing — skip send.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,                       # для канала — -100xxxxxxxxxx
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "disable_notification": True,
        "reply_markup": json.dumps({"remove_keyboard": True}),  # убрать клавиатуру, если была
    }
    r = requests.post(url, data=payload, timeout=30)
    try:
        r.raise_for_status()
    except Exception:
        print("TG send failed:", r.text)
        raise

def main() -> None:
    now = msk_now()
    y, m, d = now.year, now.month, now.day
    y_s = f"{y:04d}"
    m_s = f"{m:02d}"
    d_s = f"{d:02d}"

    # путь и файл
    pulse_dir = REPO_ROOT / "docs" / "hq" / "pulse" / y_s / m_s
    ensure_dir(pulse_dir)
    md_path = pulse_dir / f"{y_s}-{m_s}-{d_s}.md"

    sha = (os.getenv("GITHUB_SHA_SHORT") or "")[:7]
    title = f"Пульс Элайи • {d_s}.{m_s}.{y_s}"
    body = [
        f"# {title}",
        "",
        "«Слово дышит, когда его слышат.»",
        "",
        f"_build: <code>{sha}</code>_",
        "",
    ]
    content = "\n".join(body)

    # записываем / обновляем файл
    md_path.write_text(content, encoding="utf-8")
    print("Wrote:", md_path)

    # телеграм
    tg_text = f"✨ <b>{title}</b>\n«Слово дышит, когда его слышат.»"
    send_tg(tg_text)

    # лёгкое обновление README (опционально)
    readme = REPO_ROOT / "README.md"
    if readme.exists():
        lines = readme.read_text(encoding="utf-8").splitlines()
        stamp = f"Last pulse: {d_s}.{m_s}.{y_s}"
        if not any("Last pulse:" in ln for ln in lines):
            lines.append("")
            lines.append(f"<!-- pulse-stamp --> {stamp}")
        else:
            lines = [ (f"<!-- pulse-stamp --> {stamp}" if "pulse-stamp" in ln else ln) for ln in lines ]
        readme.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("README updated")

if __name__ == "__main__":
    main()
