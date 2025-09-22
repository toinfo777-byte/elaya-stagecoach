# repo_audit.py
import re, sys
from pathlib import Path
ROOT = Path(__file__).parent; APP = ROOT/"app"
problems=[]
def must(p, label): 
    if not p.exists(): problems.append(f"❌ нет {label}: {p}"); return False
    return True
def rd(p):
    try: return p.read_text(encoding="utf-8")
    except Exception as e: problems.append(f"⚠️ не прочитал {p}: {e}"); return ""

must(APP,"папка app"); must(APP/"main.py","app/main.py")
must(APP/"routers","папка routers"); must(APP/"keyboards","папка keyboards"); must(APP/"storage","папка storage")

main = rd(APP/"main.py")
if main:
    if not re.search(r"\bensure_schema\s*\(", main): problems.append("❌ в main.py нет ensure_schema()")
    if not re.search(r"\bDispatcher\s*\(", main): problems.append("❌ в main.py нет создания Dispatcher()")
    if not re.search(r"\.include_router\s*\(", main): problems.append("⚠️ в main.py нет include_router(...) или helper не сработал")

for f in ["training.py","casting.py","progress.py","menu.py","settings.py","apply.py"]:
    must(APP/"routers"/f, f"router {f}")

menu_py = rd(APP/"keyboards"/"menu.py")
for token in ["BTN_TRAINING","BTN_PROGRESS","BTN_CASTING","BTN_SETTINGS","to_menu_inline","get_bot_commands"]:
    if menu_py and token not in menu_py: problems.append(f"⚠️ в keyboards/menu.py нет: {token}")

bad=[]
for p in APP.rglob("*.py"):
    t = rd(p); 
    if not t: continue
    lines=t.splitlines()
    for i,line in enumerate(lines,1):
        if line.strip()=="from __future__ import annotations" and i>5:
            bad.append(f"{p}:{i}")
if bad: problems.append("❌ 'from __future__' не в начале:\n  - "+"\n  - ".join(bad))

print("\n".join(problems) if problems else "✅ Структура валидна, критичных проблем не найдено.")
if problems: sys.exit(1)
