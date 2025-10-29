from app.scene.manager import SceneManager

def test_cycle_order():
    sm = SceneManager()
    assert sm.get_current_scene() is None

    first = sm.enter_scene("scene_intro")
    assert first == "scene_intro"
    assert sm.get_current_scene() == "scene_intro"

    assert sm.next_scene() == "scene_reflect"
    assert sm.next_scene() == "scene_transition"
    # цикл
    assert sm.next_scene() == "scene_intro"

def test_get_config_defaults():
    from app.scene import config as cfg
    sm = SceneManager()
    sm.enter_scene("scene_reflect")
    conf = sm.get_config()
    assert conf.time == cfg.REFLECT.time
    assert conf.duration_sec == cfg.REFLECT.duration_sec
