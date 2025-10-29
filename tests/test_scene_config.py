import os
from importlib import reload

def test_defaults():
    # Чистим ENV, чтобы проверить значения по умолчанию
    for k in [
        "SCENE_INTRO_TIME", "SCENE_INTRO_DURATION", "SCENE_INTRO_REPLY",
        "SCENE_REFLECT_TIME", "SCENE_REFLECT_DURATION", "SCENE_REFLECT_REPLY",
        "SCENE_TRANSITION_TIME", "SCENE_TRANSITION_DURATION", "SCENE_TRANSITION_REPLY",
    ]:
        os.environ.pop(k, None)

    from app.scene import config as cfg
    reload(cfg)

    assert cfg.INTRO.time == "09:00"
    assert cfg.INTRO.duration_sec == 180
    assert cfg.INTRO.reply_mode == "text"

    assert cfg.REFLECT.time == "21:00"
    assert cfg.REFLECT.duration_sec == 300
    assert cfg.REFLECT.reply_mode == "text"

    assert cfg.TRANSITION.time == "22:30"
    assert cfg.TRANSITION.duration_sec == 180
    assert cfg.TRANSITION.reply_mode == "text"

def test_env_overrides(monkeypatch):
    monkeypatch.setenv("SCENE_INTRO_TIME", "08:45")
    monkeypatch.setenv("SCENE_INTRO_DURATION", "240")
    monkeypatch.setenv("SCENE_INTRO_REPLY", "buttons")

    from app.scene import config as cfg
    reload(cfg)

    assert cfg.INTRO.time == "08:45"
    assert cfg.INTRO.duration_sec == 240
    assert cfg.INTRO.reply_mode == "buttons"
