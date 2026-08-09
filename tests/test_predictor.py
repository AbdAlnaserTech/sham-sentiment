"""اختبارات BertSentimentPredictor — التحميل والتنبؤ."""

import os

import pytest

from config import load_config
from models.bert_predictor import BERT_AVAILABLE, BertNotAvailableError, load_bert_predictor
from models.registry import load_predictor


def test_config_loads_defaults():
    """تحميل الإعدادات — max_text_length و confidence_threshold."""
    config = load_config()
    assert config.max_text_length > 0
    assert config.confidence_threshold > 0


@pytest.mark.skipif(not BERT_AVAILABLE, reason="transformers/torch not installed")
def test_load_bert_predictor():
    """تحميل BERT عبر registry."""
    try:
        predictor = load_predictor()
    except BertNotAvailableError:
        pytest.skip("BERT models not downloaded")
    assert predictor is not None


@pytest.mark.skipif(not BERT_AVAILABLE, reason="transformers/torch not installed")
def test_predict_positive_english():
    """تنبؤ على تعليق إنجليزي."""
    try:
        predictor = load_predictor()
    except BertNotAvailableError:
        pytest.skip("BERT models not downloaded")
    result = predictor.predict_with_confidence(
        "I genuinely loved the product; it exceeded my expectations.",
        language="en",
    )
    assert result["sentiment"] in {"positive", "negative", "neutral"}
    assert 0 <= result["confidence"] <= 100
    assert "distribution" in result


@pytest.mark.skipif(not BERT_AVAILABLE, reason="transformers/torch not installed")
def test_predict_rejects_empty_text():
    """رفض نص فارغ."""
    try:
        predictor = load_bert_predictor()
    except BertNotAvailableError:
        pytest.skip("BERT models not downloaded")
    with pytest.raises(ValueError):
        predictor.predict_with_confidence("   ")
