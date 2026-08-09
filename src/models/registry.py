"""
تحميل نموذج BERT — نقطة الدخول الوحيدة للتنبؤ.

الواجهة و CLI و API تستدعي: load_predictor()
"""

from models.bert_predictor import (
    BERT_AVAILABLE,
    BertNotAvailableError,
    BertSentimentPredictor,
    finetuned_model_available,
    load_bert_predictor,
)
from config import load_config

PredictorType = BertSentimentPredictor


def load_predictor(root_dir: str | None = None) -> PredictorType:
    """يحمّل BertSentimentPredictor (XLM-RoBERTa + fallbacks)."""
    config = load_config()
    threshold = float(config.inference.get("bert_neutral_threshold", 0.58))
    return load_bert_predictor(neutral_threshold=threshold, root_dir=root_dir)


def available_models(root_dir: str | None = None) -> dict[str, dict]:
    """قائمة النموذج المتاح — BERT فقط."""
    _ = root_dir
    return {
        "bert": {
            "label": "XLM-RoBERTa (BERT)",
            "available": BERT_AVAILABLE,
            "description": (
                "BERT Fine-tuned على بيانات المشروع"
                if finetuned_model_available(root_dir)
                else "BERT multilingual — XLM-RoBERTa"
            ),
        },
    }


__all__ = [
    "BertNotAvailableError",
    "BertSentimentPredictor",
    "PredictorType",
    "available_models",
    "load_predictor",
]
