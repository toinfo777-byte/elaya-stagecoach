import os
import sys
import importlib
import pytest

SCENE_ENV_KEYS = [
    "SCENE_INTRO_TIME", "SCENE_INTRO_DURATION", "SCENE_INTRO_REPLY",
    "SCENE_REFLECT_TIME", "SCENE_REFLECT_DURATION", "SCENE_REFLECT_REPLY",
    "SCENE_TRANSITION_TIME", "SCENE_TRANSITION_DURATION", "SCENE_TRANSITION_REPLY",
]

def _reload_cfg():
    """Жёстко пересобираем модуль конфига после смены ENV."""
    sys.modules.pop("app.scene.config", None)
    from app.scene import config as cfg
    return importlib.reload(cfg)

@pytest.fixture(autouse=True)
def clean_env():
    """Сохраняем/очищаем SCENE_* перед тестом и восстанавливаем после."""
    backup = {k: os.environ.get(k) for k in SCENE_ENV_KEYS}
    for k in SCENE_ENV_KEYS:
        os.environ.pop(k, None)
    try:
        yield
    finally:
        for k, v in backup.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

def test_defaults():
    cfg = _reload_cfg()

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

    cfg = _reload_cfg()

    assert cfg.INTRO.time == "08:45"
    assert cfg.INTRO.duration_sec == 240
    assert cfg.INTRO.reply_mode == "buttons"

def test_invalid_duration_falls_back_to_default(monkeypatch):
    # duration не int → должно вернуться значение по умолчанию (180)
    monkeypatch.setenv("SCENE_INTRO_DURATION", "not_an_int")
    cfg = _reload_cfg()
    assert cfg.INTRO.duration_sec == 180
