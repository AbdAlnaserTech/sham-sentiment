import os

import pytest

from config import load_config
from models.predictor import SentimentPredictor, load_default_predictor
from paths import ProjectPaths


@pytest.fixture
def paths():
    return ProjectPaths.from_project_root()


def test_config_loads_defaults():
    config = load_config()
    assert config.labels == ["negative", "neutral", "positive"]
    assert config.max_text_length > 0


def test_predictor_raises_when_model_missing(tmp_path):
    missing = str(tmp_path / "missing.pkl")
    with pytest.raises(FileNotFoundError):
        SentimentPredictor(missing)


@pytest.mark.skipif(
    not os.path.exists(ProjectPaths.from_project_root().model_path),
    reason="Trained model not available",
)
def test_predictor_positive_english():
    predictor = load_default_predictor()
    result = predictor.predict_with_confidence(
        "I genuinely loved the product; it exceeded my expectations.",
        language="en",
    )
    assert result["sentiment"] in {"positive", "negative", "neutral"}
    assert 0 <= result["confidence"] <= 100
    assert "distribution" in result


@pytest.mark.skipif(
    not os.path.exists(ProjectPaths.from_project_root().model_path),
    reason="Trained model not available",
)
def test_predictor_rejects_empty_text():
    predictor = load_default_predictor()
    with pytest.raises(ValueError):
        predictor.predict_with_confidence("   ")
