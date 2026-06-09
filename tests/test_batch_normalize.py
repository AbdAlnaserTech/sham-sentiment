import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from components.batch_results import normalize_batch_result, normalize_batch_results, results_to_dataframe


def test_normalize_batch_result_fills_missing_language():
    item = {"text": "الخدمة ممتازة", "sentiment": "positive", "confidence": 90.0}
    normalized = normalize_batch_result(item)
    assert normalized["language"]
    assert normalized["sentiment"] == "positive"


def test_results_to_dataframe_empty_has_columns():
    df = results_to_dataframe([])
    assert "language" in df.columns
    assert "sentiment" in df.columns


def test_normalize_batch_results_preserves_count():
    raw = [{"text": "hello"}, {"text": "world", "sentiment": "positive", "language": "en"}]
    normalized = normalize_batch_results(raw, ["hello", "world"])
    assert len(normalized) == 2
    assert all(item.get("language") for item in normalized)
