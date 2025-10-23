#!/usr/bin/env python3
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
DOCS = ROOT / "docs" / "elaya_status"

def find_last_report():
    files = sorted(DOCS.glob("Elaya_Status_*.md"))
    return files[-1].name if files else None

def build_block(latest: str | None) -> str:
    if not latest:
        return ("🪶 Last report → [N/A](docs/elaya_status/)\n"
                "![System Alive](https://img.shields.io/badge/system-unknown-lightgrey)")
    return (f"🪶 Last report → [{latest}](docs/elaya_status/{latest})\n"
            f"![System Alive](https://img.shields.io/badge/system-alive-brightgreen)")

def main():
    md = README.read_text(encoding="utf-8")
    latest = find_last_report()
    new_block = build_block(latest)
    md = re.sub(
        r"<!-- STATUS_BLOCK_START -->.*?<!-- STATUS_BLOCK_END -->",
        f"<!-- STATUS_BLOCK_START -->\n{new_block}\n<!-- STATUS_BLOCK_END -->",
        md,
        flags=re.S,
    )
    README.write_text(md, encoding="utf-8")
    print("Updated README status block →", latest or "N/A")

if __name__ == "__main__":
    main()
