from fastapi.testclient import TestClient
from task3_meeting_to_scope.main import app

def test_health():
    with TestClient(app) as client:
        response=client.get("/health")
        assert response.status_code==200
        assert response.json()["status"]=="ok"

def test_compare_requires_baseline():
    with TestClient(app) as client:
        response=client.post("/compare",json={"project_id":"demo-1","transcript":"We need better product search and mobile filters."})
        assert response.status_code==400
