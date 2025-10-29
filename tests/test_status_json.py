from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_status_json_fields():
    r = client.get("/status_json")
    assert r.status_code == 200
    data = r.json()

    # базовые ключи
    for key in ["env", "mode", "service", "build", "uptime"]:
        assert key in data, f"missing {key}"

    # HQ-поля
    for key in ["status_emoji", "status_word", "focus", "note", "quote"]:
        assert key in data, f"missing {key}"

    print("✅ /status_json OK —", data)
