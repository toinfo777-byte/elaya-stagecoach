from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_status_json_fields():
    r = client.get("/status_json")
    assert r.status_code == 200
    data = r.json()
    # обязательные поля
    must = {"env", "mode", "service", "build", "sha", "uptime"}
    assert must.issubset(data.keys())
    assert data["service"] in ("web", "worker")
    assert isinstance(data["uptime"], int) or str(data["uptime"]).endswith("h")
