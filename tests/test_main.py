from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_words():
    response = client.get("/words/easy")
    assert response.status_code == 200

def test_update_progress():
    response = client.post("/progress/", json={"user_id": 1, "word_id": 1, "known": True})
    assert response.status_code == 200
    assert response.json()["message"] == "Progress updated"
