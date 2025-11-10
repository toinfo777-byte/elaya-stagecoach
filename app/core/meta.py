from __future__ import annotations
import yaml, os
from pathlib import Path

META_PATH = Path(__file__).resolve().parent.parent / "assets" / "meta.yaml"

class Meta:
    def __init__(self):
        self.data = {}
        if META_PATH.exists():
            with open(META_PATH, "r", encoding="utf-8") as f:
                self.data = yaml.safe_load(f)

    def get(self, *path, default=None):
        ref = self.data
        for key in path:
            ref = ref.get(key) if isinstance(ref, dict) else None
            if ref is None:
                return default
        return ref

    @property
    def name(self): return self.get("identity", "name")
    @property
    def motto(self): return self.get("identity", "motto")
    @property
    def palette(self): return self.get("theme", "palette")

meta = Meta()
