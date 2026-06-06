import os
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd

from config import AppConfig, load_config
from language import detect_language, safe_percent
from logging_utils import logger
from paths import ProjectPaths
from preprocessing import TextPreprocessor


class ModelNotFoundError(FileNotFoundError):
    pass


class SentimentPredictor:
    def __init__(
        self,
        model_path: str,
        config: AppConfig | None = None,
        preprocessor: TextPreprocessor | None = None,
    ) -> None:
        if not os.path.exists(model_path):
            raise ModelNotFoundError(
                f"Model not found at {model_path}. Run: python train.py --data data/sentiment_dataset_multilingual.csv"
            )

        self.model_path = model_path
        self.model = joblib.load(model_path)
        self.config = config or load_config()
        self.pre = preprocessor or TextPreprocessor(remove_stopwords=True)

    def predict_with_confidence(self, text: str, language: Optional[str] = None) -> Dict[str, Any]:
        if not text or not text.strip():
            raise ValueError("Text must not be empty.")

        max_len = self.config.max_text_length
        if len(text) > max_len:
            raise ValueError(f"Text exceeds maximum length of {max_len} characters.")

        lang = language or detect_language(text)
        cleaned = self.pre.preprocess(text, language=lang).cleaned_text

        probas = self.model.predict_proba([cleaned])[0]
        classes = self.model.classes_
        best_idx = int(np.argmax(probas))
        label = str(classes[best_idx])
        confidence = safe_percent(float(probas[best_idx]) * 100.0)
        threshold = self.config.confidence_threshold

        distribution = {
            str(cls): safe_percent(float(prob) * 100.0)
            for cls, prob in zip(classes, probas)
        }

        return {
            "text": text,
            "language": lang,
            "cleaned_text": cleaned,
            "sentiment": label,
            "confidence": confidence,
            "distribution": distribution,
            "is_reliable": confidence >= threshold,
            "confidence_threshold": threshold,
        }

    def predict_batch(
        self,
        texts: List[str],
        languages: Optional[List[Optional[str]]] = None,
        auto_language: bool = True,
    ) -> List[Dict[str, Any]]:
        if not texts:
            return []

        languages = languages or [None] * len(texts)
        cleaned_rows: List[str] = []
        resolved_langs: List[str] = []
        valid_indices: List[int] = []
        results: List[Dict[str, Any]] = [{} for _ in texts]
        threshold = self.config.confidence_threshold

        for index, (text, lang) in enumerate(zip(texts, languages)):
            raw = str(text or "").strip()
            if not raw:
                results[index] = {
                    "text": text,
                    "language": lang or "en",
                    "cleaned_text": "",
                    "sentiment": "neutral",
                    "confidence": 0.0,
                    "distribution": {},
                    "is_reliable": False,
                    "error": "Empty comment",
                }
                continue

            if len(raw) > self.config.max_text_length:
                results[index] = {
                    "text": text,
                    "language": lang or detect_language(raw),
                    "cleaned_text": "",
                    "sentiment": "neutral",
                    "confidence": 0.0,
                    "distribution": {},
                    "is_reliable": False,
                    "error": f"Text exceeds maximum length of {self.config.max_text_length}",
                }
                continue

            resolved = lang if lang and not auto_language else (lang or detect_language(raw))
            cleaned = self.pre.preprocess(raw, language=resolved).cleaned_text
            cleaned_rows.append(cleaned)
            resolved_langs.append(resolved)
            valid_indices.append(index)
            results[index] = {"text": raw}

        if not cleaned_rows:
            return results

        probas = self.model.predict_proba(cleaned_rows)
        classes = self.model.classes_

        for row_index, source_index in enumerate(valid_indices):
            probs = probas[row_index]
            best_idx = int(np.argmax(probs))
            label = str(classes[best_idx])
            confidence = safe_percent(float(probs[best_idx]) * 100.0)
            distribution = {
                str(cls): safe_percent(float(prob) * 100.0)
                for cls, prob in zip(classes, probs)
            }
            results[source_index] = {
                "text": results[source_index]["text"],
                "language": resolved_langs[row_index],
                "cleaned_text": cleaned_rows[row_index],
                "sentiment": label,
                "confidence": confidence,
                "distribution": distribution,
                "is_reliable": confidence >= threshold,
                "confidence_threshold": threshold,
            }

        return results

    def predict_dataframe(
        self,
        df: pd.DataFrame,
        text_col: str = "text",
        language_col: str | None = "language",
        auto_language: bool = True,
    ) -> pd.DataFrame:
        texts = [str(value) for value in df[text_col].tolist()]
        languages: List[Optional[str]] = []
        if language_col and language_col in df.columns:
            languages = [
                str(value) if pd.notna(value) else None
                for value in df[language_col].tolist()
            ]
        else:
            languages = [None] * len(texts)

        return pd.DataFrame(
            self.predict_batch(texts, languages=languages, auto_language=auto_language)
        )


def load_default_predictor(
    root_dir: str | None = None,
    config: AppConfig | None = None,
) -> SentimentPredictor:
    paths = ProjectPaths.from_project_root(root_dir)
    logger.info("Loading model from %s", paths.model_path)
    return SentimentPredictor(paths.model_path, config=config)
