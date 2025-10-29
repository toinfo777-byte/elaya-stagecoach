from typing import Optional, Tuple
from . import config as scene_cfg

class SceneManager:
    def __init__(self):
        self.current_scene: Optional[str] = None
        self.scenes_order = ["scene_intro", "scene_reflect", "scene_transition"]

    def enter_scene(self, name: str) -> str:
        if name in self.scenes_order:
            self.current_scene = name
        return self.current_scene or self.scenes_order[0]

    def next_scene(self) -> str:
        if not self.current_scene:
            self.current_scene = self.scenes_order[0]
            return self.current_scene
        idx = self.scenes_order.index(self.current_scene)
        self.current_scene = self.scenes_order[(idx + 1) % len(self.scenes_order)]
        return self.current_scene

    def get_current_scene(self) -> Optional[str]:
        return self.current_scene

    def get_config(self, name: Optional[str] = None):
        key = name or self.current_scene
        if not key:
            key = self.scenes_order[0]
        return scene_cfg.ALL.get(key)

scene_manager = SceneManager()
