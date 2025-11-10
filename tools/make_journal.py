from __future__ import annotations
import sqlite3, os
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/data/elaya.db")
OUT_DIR = "docs/hq/journal"

def fetch_rows():
    with sqlite3.connect(DB_PATH) as con:
        cur = con.execute("SELECT user_id,last_scene,last_reflect,updated_at FROM scene_state")
        return cur.fetchall()

def make_md(rows):
    d = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [f"# 🌙 Журнал дыхания — {d}", ""]
    if not rows:
        lines.append("_нет активных записей_")
    for (uid, scene, reflect, upd) in rows:
        lines.append(f"— **user {uid}** → *{scene}* @ {upd}")
        if reflect:
            lines.append(f"  > {reflect}")
        lines.append("")
    lines.append("\n🕊 Сформировано автоматически Elaya HQ")
    return "\n".join(lines)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = fetch_rows()
    text = make_md(rows)
    d = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = f"{OUT_DIR}/Journal_{d}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[✓] Journal saved to {path}")
    return path

if __name__ == "__main__":
    main()
