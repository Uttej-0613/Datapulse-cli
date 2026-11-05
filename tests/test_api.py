from fastapi.testclient import TestClient
from datapulse.api import app
import datapulse.database as database
import datapulse.sql_guard as sql_guard


def test_health_and_ready(monkeypatch, tmp_path):
    target = tmp_path / "api.db"
    monkeypatch.setattr(database, "DB_PATH", target)
    monkeypatch.setattr(sql_guard, "DB_PATH", target)
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/ready").status_code == 200


def test_csv_upload_and_query(monkeypatch, tmp_path):
    target = tmp_path / "api.db"
    monkeypatch.setattr(database, "DB_PATH", target)
    monkeypatch.setattr(sql_guard, "DB_PATH", target)
    with TestClient(app) as client:
        response = client.post("/ingest", files={"file": ("people.csv", b"name,age\\nAda,36\\n", "text/csv")})
        assert response.status_code == 200
        assert response.json()["rows"] == 1
        query = client.post("/query", json={"sql": "SELECT name, age FROM people"})
        assert query.status_code == 200
        assert query.json()["rows"] == [{"name": "Ada", "age": 36}]


def test_api_key_protects_data_routes(monkeypatch):
    monkeypatch.setenv("DATAPULSE_API_KEY", "test-secret")
    monkeypatch.setenv("ENVIRONMENT", "test")
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/tables").status_code == 401
        assert client.get("/tables", headers={"X-API-Key": "test-secret"}).status_code == 200
