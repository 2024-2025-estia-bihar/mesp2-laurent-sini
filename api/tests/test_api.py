from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_predict():
    response = client.get("/predict")
    assert response.status_code == 200
    assert "message" in response.json()

