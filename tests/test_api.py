import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.ai_service import AIService

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"

def test_login_demo():
    response = client.post(
        "/api/auth/login",
        json={"email": "author@test.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "author"

@pytest.mark.asyncio
async def test_ai_classification_fallback():
    res = await AIService.analyze_and_draft(
        subject="Delay in October royalty payout",
        description="I have not received my royalty payment for BK001"
    )
    assert res["classification"] == "Royalty & Payouts"
    assert res["priority"] in ["Urgent", "High", "Medium"]
    assert "reply_draft" in res
