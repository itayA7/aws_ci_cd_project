from fastapi.testclient import TestClient

from main import app, entries

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert "Welcome" in r.json()["message"]


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_ready():
    assert client.get("/ready").status_code == 200


def test_version():
    assert "version" in client.get("/version").json()


def test_create_and_list_entries():
    entries.clear()
    r = client.post("/entries", json={"message": "hello"})
    assert r.status_code == 201

    client.post("/entries", json={"message": "world"})
    messages = [e["message"] for e in client.get("/entries").json()]
    assert messages == ["world", "hello"]


def test_empty_message_rejected():
    assert client.post("/entries", json={"message": ""}).status_code == 422
