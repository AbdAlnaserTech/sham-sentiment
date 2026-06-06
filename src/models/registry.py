from typing import Literal, Union

from config import load_config
from logging_utils import logger
from models.bert_predictor import BertNotAvailableError, BertSentimentPredictor, load_bert_predictor
from models.predictor import SentimentPredictor, load_default_predictor
from paths import ProjectPaths

ModelKind = Literal["tfidf", "bert"]
PredictorType = Union[SentimentPredictor, BertSentimentPredictor]


def _bert_description(root_dir: str | None) -> str:
    from models.bert_predictor import finetuned_model_available

    if finetuned_model_available(root_dir):
        return "BERT Fine-tuned على بيانات المشروع — أعلى دقة | موصى به للمناقشة"
    return "BERT multilingual — F1≈76% على Demo | Fine-tune: python finetune_bert.py"


def load_predictor(
    model_kind: ModelKind = "tfidf",
    root_dir: str | None = None,
) -> PredictorType:
    if model_kind == "bert":
        try:
            config = load_config()
            threshold = float(config.inference.get("bert_neutral_threshold", 0.58))
            return load_bert_predictor(neutral_threshold=threshold, root_dir=root_dir)
        except BertNotAvailableError:
            logger.warning("BERT unavailable, falling back to TF-IDF")
            return load_default_predictor(root_dir=root_dir)

    return load_default_predictor(root_dir=root_dir)


def available_models(root_dir: str | None = None) -> dict[str, dict]:
    paths = ProjectPaths.from_project_root(root_dir)
    models = {
        "tfidf": {
            "label": "TF-IDF + LogReg (سريع)",
            "available": __import__("os").path.exists(paths.model_path),
            "description": "Logistic Regression — F1≈67% على أمثلة العرض | LIME",
        },
        "bert": {
            "label": "XLM-RoBERTa (الأدق — موصى به)",
            "available": True,
            "description": _bert_description(root_dir),
        },
    }
    try:
        from models.bert_predictor import BERT_AVAILABLE

        models["bert"]["available"] = BERT_AVAILABLE
    except ImportError:
        models["bert"]["available"] = False
    return models
