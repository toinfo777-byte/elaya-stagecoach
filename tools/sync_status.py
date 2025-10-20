# tools/sync_status.py
import os, json, re, datetime, sys
from pathlib import Path

DOC = Path("docs/Elaya_Current_Status_Q4_2025.md")
LOG = Path("tools/sync_status.log")

BUILD_MARK = os.getenv("BUILD_MARK", "").strip()
GIT_SHA = (os.getenv("SHORT_SHA", "") or os.getenv("GITHUB_SHA", "")).strip()
ENV = os.getenv("ENV", "develop").strip()
IMAGE_TAG = os.getenv("IMAGE_TAG", "").strip()

def load_event():
    """Поддержка repository_dispatch и workflow_dispatch."""
    event_path = os.getenv("GH_EVENT_PATH")
    if event_path and Path(event_path).exists():
        with open(event_path, "r", encoding="utf-8") as f:
            ev = json.load(f)

        # repository_dispatch → client_payload
        pl = ev.get("client_payload") or ev.get("payload", {}).get("client_payload")
        if pl:
            return pl.get("block"), pl.get("content")

        # workflow_dispatch → inputs
        ip = ev.get("inputs") or {}
        if ip:
            return ip.get("block") or os.getenv("SYNC_BLOCK"), ip.get("content") or os.getenv("SYNC_CONTENT")

    # запасной вариант из env
    return os.getenv("SYNC_BLOCK"), os.getenv("SYNC_CONTENT")

def ensure_doc():
    if not DOC.exists():
        DOC.parent.mkdir(parents=True, exist_ok=True)
        DOC.write_text("# Элайя — Текущий статус (Q4 2025)\n\n", encoding="utf-8")

def replace_block(md: str, block_name: str, new_md: str) -> str:
    """
    Блоки помечаем маркерами:
    <!-- BLOCK:Имя -->
    ... контент ...
    <!-- END BLOCK -->
    """
    block_name = block_name.strip()
    pat = re.compile(
        rf"(<!--\s*BLOCK:{re.escape(block_name)}\s*-->)(.*?)(<!--\s*END\s+BLOCK\s*-->)",
        re.S | re.I
    )
    if pat.search(md):
        return pat.sub(rf"\1\n{new_md}\n\3", md)
    else:
        chunk = f"\n\n<!-- BLOCK:{block_name} -->\n{new_md}\n<!-- END BLOCK -->\n"
        return md + chunk

def build_block_md() -> str:
    """Готовый Build-блок, если пришли метки билда из Actions."""
    if not (BUILD_MARK or GIT_SHA or IMAGE_TAG):
        return ""
    sha7 = (GIT_SHA or "")[:7]
    now = datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    return (
        f"BUILD_MARK: `{BUILD_MARK or 'local'}`  \n"
        f"GIT_SHA: `{sha7 or 'local'}`  \n"
        f"ENV: `{ENV}`  \n"
        f"IMAGE: `{IMAGE_TAG or 'ghcr.io/unknown/elaya-stagecoach:develop'}`  \n"
        f"Updated: {now}"
    )

def log(msg: str):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.utcnow().isoformat()}Z {msg}\n")

def main():
    block, content = load_event()
    ensure_doc()

    # если пришли только метки билда — формируем стандартный Build-блок
    if (not content or not content.strip()) and (BUILD_MARK or GIT_SHA or IMAGE_TAG):
        block = block or "Build"
        content = build_block_md()

    if not content or not content.strip():
        log("no content provided; skip")
        print("No content provided. Nothing to do.")
        return

    if not block:
        block = "Изменения"

    md = DOC.read_text(encoding="utf-8")
    new_md = replace_block(md, block, content.strip())
    DOC.write_text(new_md, encoding="utf-8")

    log(f"updated: block='{block}' len={len(content)}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"ERROR: {e}")
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
