from app.scene import manager, config as scene_cfg

def test_manager_flow_and_config():
    sm = manager.SceneManager()
    assert sm.enter_scene("scene_intro") == "scene_intro"
    assert sm.next_scene() == "scene_reflect"
    assert sm.next_scene() == "scene_transition"
    assert sm.next_scene() == "scene_intro"
    # конфиг рефлексии доступен и совпадает со ссылочным
    cfg = sm.get_config("scene_reflect")
    assert cfg.time == scene_cfg.REFLECT.time
    assert isinstance(cfg.duration_sec, int)
