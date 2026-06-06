import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from data.loader import load_labeled_csv  # noqa: E402


def test_load_validation_dataset():
    path = os.path.join(ROOT, "data", "real", "validation_comments.csv")
    df = load_labeled_csv(path)
    assert len(df) >= 30
    assert set(df["sentiment"]).issubset({"positive", "negative", "neutral"})


@pytest.mark.skipif(
    not os.path.exists(os.path.join(ROOT, "models", "sentiment_model.pkl")),
    reason="Trained model not available",
)
def test_evaluate_validation():
    from evaluate import evaluate_on_labeled_csv

    path = os.path.join(ROOT, "data", "real", "validation_comments.csv")
    result = evaluate_on_labeled_csv(path, root_dir=ROOT)
    assert result["samples"] >= 30
    assert "macro avg" in result["overall"]
