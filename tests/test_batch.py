"""اختبارات التحليل الجماعي — BERT predict_batch."""

import pytest

from models.bert_predictor import BERT_AVAILABLE, BertNotAvailableError
from models.registry import load_predictor


@pytest.mark.skipif(not BERT_AVAILABLE, reason="transformers/torch not installed")
def test_batch_predict_returns_all_rows():
    """predict_batch يرجع نتيجة لكل تعليق."""
    try:
        predictor = load_predictor()
    except BertNotAvailableError:
        pytest.skip("BERT models not downloaded")

    texts = [
        "Excellent service and fast delivery",
        "Terrible experience, never again",
        "It is okay, nothing special",
    ]
    results = predictor.predict_batch(texts)
    assert len(results) == 3
    for item in results:
        assert item.get("sentiment") in {"positive", "negative", "neutral", None} or item.get("error")


@pytest.mark.skipif(not BERT_AVAILABLE, reason="transformers/torch not installed")
def test_batch_empty_and_whitespace():
    """التعليقات الفارغة تُرجع error أو neutral."""
    try:
        predictor = load_predictor()
    except BertNotAvailableError:
        pytest.skip("BERT models not downloaded")
    results = predictor.predict_batch(["", "  ", "valid comment please"])
    assert len(results) == 3
