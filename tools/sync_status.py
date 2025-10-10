# tools/sync_status.py
from __future__ import annotations
import os, base64, datetime
from pathlib import Path
from github import Github

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None  # для Python < 3.9

REPO_NAME  = os.getenv("GITHUB_REPO", "toinfo777-byte/elaya-stagecoach")
STATUS_DIR = os.getenv("STATUS_DIR", "docs/elaya_status")
BRANCH     = os.getenv("GITHUB_BRANCH", "develop")
STAMP_PREFIX = "🕰️ Последнее обновление штаба: "

FILES = [
    "README.md",
    "Elaya_Current_Status_Q4_2025.md",
    "Elaya_Roadmap_I_Основание_света.md",
]


def _now_str() -> str:
    tz = ZoneInfo("Europe/Berlin") if ZoneInfo else None
    return datetime.datetime.now(tz=tz).strftime("%Y-%m-%d %H:%M")


def _ensure_stamp_anchor(text: str) -> str:
    if "<!--STAMP-->" not in text:
        if text and not text.endswith("\n"):
            text += "\n"
        text += f"{STAMP_PREFIX}<!--STAMP-->\n"
    return text


def _update_stamp(text: str) -> str:
    text = _ensure_stamp_anchor(text)
    return text.replace("<!--STAMP-->", _now_str())


def _read_local(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _create_or_update(repo, path: str, new_text: str, commit_message: str) -> bool:
    """True — был создан или обновлён файл, False — без изменений"""
    try:
        current = repo.get_contents(path, ref=BRANCH)
        current_text = base64.b64decode(current.content).decode("utf-8")
        if current_text != new_text:
            repo.update_file(
                path=path,
                message=commit_message,
                content=new_text,
                sha=current.sha,
                branch=BRANCH,
            )
            return True
        return False
    except Exception:
        repo.create_file(
            path=path,
            message=commit_message.replace("update:", "new:"),
            content=new_text,
            branch=BRANCH,
        )
        return True


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("❌ GITHUB_TOKEN не найден в окружении")

    gh = Github(token)
    repo = gh.get_repo(REPO_NAME)

    made_commits = False
    for name in FILES:
        local_path = Path(STATUS_DIR) / name
        if not local_path.exists():
            raise FileNotFoundError(f"Локальный файл не найден: {local_path}")

        new_text = _read_local(local_path)
        if name == "README.md":
            new_text = _update_stamp(new_text)

        repo_path = f"{STATUS_DIR}/{name}"
        commit_message = f"update: штаб Элайи — синхронизация {datetime.date.today()}"
        changed = _create_or_update(repo, repo_path, new_text, commit_message)
        made_commits = made_commits or changed

    print("✅ Синхронизация завершена — изменения зафиксированы."
          if made_commits else
          "ℹ️ Изменений нет — коммиты не создавались.")


if __name__ == "__main__":
    main()
