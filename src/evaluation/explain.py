import os
from typing import Any, Dict, List, Optional

import numpy as np

from language import detect_language


def supports_lime(predictor) -> bool:
    return (
        hasattr(predictor, "pre")
        and hasattr(predictor, "model")
        and hasattr(predictor.model, "predict_proba")
        and hasattr(predictor.model, "classes_")
    )


def _predict_proba_raw(predictor, texts: List[str], languages: Optional[List[Optional[str]]] = None):
    languages = languages or [None] * len(texts)
    cleaned_rows = []
    for text, lang in zip(texts, languages):
        raw = str(text or "").strip()
        if not raw:
            cleaned_rows.append("")
            continue
        resolved = lang or detect_language(raw)
        cleaned_rows.append(predictor.pre.preprocess(raw, language=resolved).cleaned_text)
    return predictor.model.predict_proba(cleaned_rows)


def explain_text(
    predictor,
    text: str,
    language: Optional[str] = None,
    num_features: int = 8,
) -> Dict[str, Any]:
    try:
        from lime.lime_text import LimeTextExplainer
    except ImportError as exc:
        raise ImportError("Install lime: pip install lime") from exc

    lang = language or detect_language(text)
    classes = [str(c) for c in predictor.model.classes_]
    explainer = LimeTextExplainer(class_names=classes)

    def classifier_fn(texts: List[str]) -> np.ndarray:
        langs = [lang] * len(texts)
        return _predict_proba_raw(predictor, texts, languages=langs)

    explanation = explainer.explain_instance(
        text,
        classifier_fn,
        num_features=num_features,
        top_labels=len(classes),
    )

    predicted = predictor.predict_with_confidence(text, language=lang)
    label = predicted["sentiment"]
    label_index = classes.index(label) if label in classes else 0

    weights = explanation.as_list(label=label_index)
    features = [
        {"word": word, "weight": float(weight)}
        for word, weight in weights
    ]

    return {
        "sentiment": label,
        "language": lang,
        "features": features,
        "explanation_available": True,
    }


def render_explanation_html(features: List[Dict[str, Any]]) -> str:
    parts = []
    for item in features:
        weight = float(item["weight"])
        color = "#16a34a" if weight > 0 else "#dc2626"
        word = item["word"]
        parts.append(
            f"<span style='background:{color}22;color:{color};padding:2px 6px;"
            f"margin:2px;border-radius:4px;'>{word} ({weight:+.3f})</span>"
        )
    return " ".join(parts) if parts else "<em>No explanation available</em>"
