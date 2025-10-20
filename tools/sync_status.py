import os, json, re, datetime, sys
from pathlib import Path

DOC = Path("docs/Elaya_Current_Status_Q4_2025.md")
LOG = Path("tools/sync_status.log")

def load_event():
    # 1) repository_dispatch с client_payload
    event_path = os.getenv("GH_EVENT_PATH")
    if event_path and Path(event_path).exists():
        with open(event_path, "r", encoding="utf-8") as f:
            ev = json.load(f)
        # repo_dispatch
        if ev.get("action") is None and "client_payload" in ev.get("payload", {}):
            pl = ev["payload"]["client_payload"]
            return pl.get("block"), pl.get("content")
        # workflow_dispatch
        ip = ev.get("inputs", {})
        if ip:
            return ip.get("block") or os.getenv("SYNC_BLOCK"), ip.get("content") or os.getenv("SYNC_CONTENT")
    # запасной вариант
    return os.getenv("SYNC_BLOCK"), os.getenv("SYNC_CONTENT")

def ensure_doc():
    if not DOC.exists():
        DOC.parent.mkdir(parents=True, exist_ok=True)
        DOC.write_text("# Элайя — Текущий статус (Q4 2025)\n\n", encoding="utf-8")

def replace_block(md: str, block_name: str, new_md: str) -> str:
    """
    Блоки помечаем маркерами:
    <!-- BLOCK:Блок 3 — Управляемость -->
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
        # нет блока — добавим в конец
        chunk = f"\n\n<!-- BLOCK:{block_name} -->\n{new_md}\n<!-- END BLOCK -->\n"
        return md + chunk

def log(msg: str):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.utcnow().isoformat()}Z {msg}\n")

def main():
    block, content = load_event()
    ensure_doc()
    if not content:
        log("no content provided; skip")
        print("No content provided. Nothing to do.")
        return

    # если блок не указан — пишем в раздел «Изменения»
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
