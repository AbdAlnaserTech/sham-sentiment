"""Tests for platform database and analytics."""

import gc
import os
import tempfile

import pandas as pd

from analytics.alerts import detect_batch_alerts
from analytics.keywords import extract_keywords_by_sentiment
from db.auth import hash_password, verify_password
from db.database import init_database
from db.repository import authenticate, ensure_default_users, save_batch_analysis


def test_password_hash_roundtrip():
    stored = hash_password("secret123")
    assert verify_password("secret123", stored)
    assert not verify_password("wrong", stored)


def test_auth_and_save_batch():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "test.db")
        os.environ["SENTIMENT_DB_PATH"] = db_path
        try:
            init_database(db_path)
            ensure_default_users()
            user = authenticate("admin", "Admin@2026")
            assert user is not None
            assert user["role"] == "admin"

            results = [
                {"text": "great service", "language": "en", "sentiment": "positive", "confidence": 88.0},
                {"text": "bad product", "language": "en", "sentiment": "negative", "confidence": 80.0},
            ]
            batch_id = save_batch_analysis(
                user_id=user["id"],
                title="test",
                source="unit",
                model_kind="bert",
                results=results,
            )
            assert batch_id == 1
        finally:
            gc.collect()
            os.environ.pop("SENTIMENT_DB_PATH", None)


def test_alerts_negative_spike():
    results = [{"sentiment": "negative", "confidence": 70}] * 6 + [
        {"sentiment": "positive", "confidence": 80}
    ]
    alerts = detect_batch_alerts(results, negative_threshold=0.45)
    assert any(a["alert_type"] == "negative_spike" for a in alerts)


def test_keywords_extraction():
    df = pd.DataFrame([
        {"text": "excellent fast delivery", "sentiment": "positive", "language": "en"},
        {"text": "terrible slow support", "sentiment": "negative", "language": "en"},
    ])
    keywords = extract_keywords_by_sentiment(df, top_n=5)
    assert "positive" in keywords
    assert len(keywords["positive"]) >= 1
