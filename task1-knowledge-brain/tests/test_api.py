from fastapi.testclient import TestClient
from task1_knowledge_brain.app.main import app

def test_health():
    with TestClient(app) as client:
        response=client.get("/health")
        assert response.status_code==200
        assert response.json()["status"]=="ok"

def test_unknown_question_escalates():
    with TestClient(app) as client:
        response=client.post("/query",json={"question":"What is the secret moon setting?"})
        assert response.status_code==200
        assert response.json()["needs_human"] is True
