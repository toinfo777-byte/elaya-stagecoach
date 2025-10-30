import importlib
import os
import sys

def _reload_cfg():
    if "app.scene.config" not in sys.modules:
        importlib.import_module("app.scene.config")
    cfg = sys.modules["app.scene.config"]
    return importlib.reload(cfg)


def test_defaults():
    cfg = _reload_cfg()
    assert cfg.SCENE_INTRO_TIME == "08:30"
    assert cfg.SCENE_INTRO_DURATION == 180
    assert cfg.SCENE_INTRO_REPLY == "default"


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("SCENE_INTRO_TIME", "08:45")
    monkeypatch.setenv("SCENE_INTRO_DURATION", "240")
    monkeypatch.setenv("SCENE_INTRO_REPLY", "buttons")

    cfg = _reload_cfg()
    assert cfg.SCENE_INTRO_TIME == "08:45"
    assert cfg.SCENE_INTRO_DURATION == 240
    assert cfg.SCENE_INTRO_REPLY == "buttons"


def test_invalid_duration_falls_back_to_default(monkeypatch):
    # duration не int → возвращаем значение по умолчанию
    monkeypatch.setenv("SCENE_INTRO_DURATION", "not_an_int")

    cfg = _reload_cfg()
    assert cfg.SCENE_INTRO_DURATION == 180
