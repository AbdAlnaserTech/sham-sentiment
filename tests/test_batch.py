import pytest

from models.predictor import load_default_predictor
from paths import ProjectPaths


@pytest.mark.skipif(
    not __import__("os").path.exists(ProjectPaths.from_project_root().model_path),
    reason="Trained model not available",
)
def test_predict_batch_multiple_comments():
    predictor = load_default_predictor()
    texts = [
        "I love this product",
        "الخدمة كتير منيح",
        "Terrible experience",
    ]
    results = predictor.predict_batch(texts)
    assert len(results) == 3
    assert all("sentiment" in item for item in results)
    assert all("confidence" in item for item in results)


@pytest.mark.skipif(
    not __import__("os").path.exists(ProjectPaths.from_project_root().model_path),
    reason="Trained model not available",
)
def test_predict_batch_empty_lines():
    predictor = load_default_predictor()
    results = predictor.predict_batch(["", "  ", "valid comment please"])
    assert len(results) == 3
    assert results[0].get("error") == "Empty comment"
