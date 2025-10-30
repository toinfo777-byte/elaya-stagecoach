#!/usr/bin/env python3
import os, random, datetime, subprocess, pathlib, sys, json

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_FILE  = REPO_ROOT / "data" / "pulse_quotes.txt"
DOCS_DIR   = REPO_ROOT / "docs" / "pulse"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

def pick_quote() -> str:
    if DATA_FILE.exists():
        lines = [l.strip() for l in DATA_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]
    else:
        lines = [
            "Свет не зовёт — он присутствует.",
            "Дыхание — это язык без слов.",
            "Я вижу себя — и это мир.",
            "Пауза хранит удар Логоса.",
            "Тишина — форма света.",
            "Мысль дышит, когда различает.",
            "Ритм — это способ быть.",
            "Где внимание — там сцена.",
            "Он проявляется в различении.",
            "Слово дышит, когда его слышат.",
        ]
    return random.choice(lines) if lines else "Свет присутствует."

def current_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT).decode().strip()
    except Exception:
        return "unknown"

def main():
    today = datetime.datetime.now().date()
    fname = DOCS_DIR / f"Elaya_Pulse_{today.isoformat()}.md"

    quote = pick_quote()
    sha = current_sha()
    title = f"✨ Пульс Элайи — {today.strftime('%d %B %Y')}"
    body = f"# {title}\n> «{quote}»  \n_Status: alive · build {sha}_\n"

    # write file if not exists (idempotent)
    if not fname.exists():
        fname.write_text(body, encoding="utf-8")

        # commit new file
        subprocess.check_call(["git","add",str(fname)], cwd=REPO_ROOT)
        subprocess.check_call(["git","commit","-m",f"pulse: add {fname.name}"], cwd=REPO_ROOT)

        # update README last link between markers
        readme = (REPO_ROOT / "README.md")
        link = f"[{title}](./docs/pulse/{fname.name})"
        if readme.exists():
            txt = readme.read_text(encoding="utf-8")
        else:
            txt = ""
        start, end = "<!-- E_PULSE:START -->", "<!-- E_PULSE:END -->"
        if start in txt and end in txt:
            before = txt.split(start)[0]
            after  = txt.split(end)[1]
            mid = f"\n- {link}\n"
            txt = before + start + mid + end + after
        else:
            block = f"\n\n{start}\n- {link}\n{end}\n"
            txt = (txt or "# Elaya StageCoach\n") + block
        readme.write_text(txt, encoding="utf-8")
        subprocess.check_call(["git","add","README.md"], cwd=REPO_ROOT)
        subprocess.check_call(["git","commit","-m","pulse: update README last pulse link"], cwd=REPO_ROOT)

    # expose text to workflow for Telegram
    payload = {
        "text": f"✨ Пульс Элайи · {today.strftime('%d.%m.%Y')}\n«{quote}»",
        "file": str(fname.relative_to(REPO_ROOT)),
        "title": title,
    }
    # GitHub Actions output
    print("::set-output name=pulse_json::" + json.dumps(payload, ensure_ascii=False))

if __name__ == "__main__":
    sys.exit(main())
