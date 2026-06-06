import os
import sys

import pytest
from fastapi.testclient import TestClient

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from api.server import app  # noqa: E402


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.skipif(
    not os.path.exists(os.path.join(ROOT, "models", "sentiment_model.pkl")),
    reason="Trained model not available",
)
def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.skipif(
    not os.path.exists(os.path.join(ROOT, "models", "sentiment_model.pkl")),
    reason="Trained model not available",
)
def test_analyze_one(client):
    response = client.post(
        "/api/v1/analyze",
        json={"text": "I love this product", "explain": False},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment"] in {"positive", "negative", "neutral"}
    assert "confidence" in data


@pytest.mark.skipif(
    not os.path.exists(os.path.join(ROOT, "models", "sentiment_model.pkl")),
    reason="Trained model not available",
)
def test_analyze_batch(client):
    response = client.post(
        "/api/v1/batch",
        json={"texts": ["great service", "bad experience", "okay product"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 3
    assert len(data["results"]) == 3
