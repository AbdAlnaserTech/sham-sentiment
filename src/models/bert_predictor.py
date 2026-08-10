"""
نموذج BERT / Transformer لتصنيف المشاعر.

ترتيب الاستخدام في predict_with_confidence:
  1) Fine-tuned محلي (models/bert_finetuned/)
  2) دمج XLM-RoBERTa + CAMeLBERT للعربي
  3) XLM-RoBERTa متعدد اللغات
  4) Twitter-RoBERTa للإنجليزي
  5) CAMeLBERT للعربي
"""

import os
from typing import Any, Dict, List, Optional

from language import detect_language, safe_percent
from logging_utils import logger

# ── بلوك 1: حالة المكتبات والـ pipelines المخزّنة (singleton) ───────────────
# كل pipeline يُحمّل مرة واحدة فقط لتجنب بطء إعادة التحميل
BERT_AVAILABLE = False
_MULTI_PIPELINE = None   # XLM-RoBERTa متعدد اللغات
_EN_PIPELINE = None      # Twitter-RoBERTa للإنجليزي
_AR_PIPELINE = None      # CAMeLBERT للعربي

try:
    from transformers import pipeline

    BERT_AVAILABLE = True
except ImportError:
    pipeline = None

# ── بلوك 2: معرّفات نماذج HuggingFace ───────────────────────────────────────
EN_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
AR_MODEL = "CAMeL-Lab/bert-base-arabic-camelbert-mix-sentiment"
MULTI_MODEL = "cardiffnlp/twitter-xlm-roberta-base-sentiment"

_FINETUNED_PIPELINE = None  # نموذج fine-tune محلياً في models/bert_finetuned/


def _cloud_light_mode() -> bool:
    """وضع خفيف للسحابة — يعطّل دمج نموذجين للعربي."""
    try:
        from cloud_setup import is_cloud_light_mode

        return is_cloud_light_mode()
    except ImportError:
        return os.environ.get("SENTIMENT_CLOUD_LIGHT", "").strip().lower() in {"1", "true", "yes"}


def _finetuned_model_dir(root_dir: str | None = None) -> str:
    """مسار مجلد النموذج الم fine-tune محلياً."""
    from paths import ProjectPaths

    paths = ProjectPaths.from_project_root(root_dir)
    return os.path.join(paths.models_dir, "bert_finetuned")


def _get_finetuned_pipeline(root_dir: str | None = None):
    """تحميل pipeline من models/bert_finetuned/ (lazy singleton)."""
    global _FINETUNED_PIPELINE
    if _FINETUNED_PIPELINE is None:
        if not BERT_AVAILABLE:
            raise BertNotAvailableError("Install transformers and torch: pip install -r requirements.txt")
        model_dir = _finetuned_model_dir(root_dir)
        if not os.path.isdir(model_dir) or not os.path.exists(os.path.join(model_dir, "config.json")):
            raise BertNotAvailableError("Fine-tuned model not found. Run: python finetune_bert.py")
        logger.info("Loading fine-tuned BERT from: %s", model_dir)
        _FINETUNED_PIPELINE = pipeline(
            "sentiment-analysis",
            model=model_dir,
            tokenizer=model_dir,
            top_k=None,
            truncation=True,
        )
    return _FINETUNED_PIPELINE


def finetuned_model_available(root_dir: str | None = None) -> bool:
    """التحقق من وجود نموذج fine-tuned ومفعّل في config."""
    from config import load_config

    try:
        config = load_config()
        if not bool(config.inference.get("use_finetuned", False)):
            return False
    except Exception:
        return False
    model_dir = _finetuned_model_dir(root_dir)
    return os.path.isdir(model_dir) and os.path.exists(os.path.join(model_dir, "config.json"))


# ── بلوك 3: توحيد تسميات النماذج المختلفة إلى 3 فئات ───────────────────────
# كل نموذج HuggingFace قد يستخدم pos/neg/neu أو label_0/1/2
LABEL_NORMALIZE = {
    "positive": "positive",
    "negative": "negative",
    "neutral": "neutral",
    "pos": "positive",
    "neg": "negative",
    "neu": "neutral",
    "label_0": "negative",
    "label_1": "neutral",
    "label_2": "positive",
}


class BertNotAvailableError(ImportError):
    """transformers/torch غير متاح أو النماذج غير منزّلة."""
    pass


def _normalize_label(raw: str) -> str:
    """تحويل تسمية النموذج إلى positive/negative/neutral."""
    key = str(raw).strip().lower().replace(" ", "_")
    return LABEL_NORMALIZE.get(key, key)


def _split_pipeline_outputs(outputs: Any, expected_count: int) -> Optional[List[List[Dict[str, Any]]]]:
    """
    تقسيم مخرجات pipeline HuggingFace إلى قائمة لكل نص في الدفعة.

    transformers قد يرجع أشكالاً مختلفة حسب batch_size و top_k.
    """
    if not outputs or expected_count <= 0 or not isinstance(outputs, list):
        return None

    if expected_count == 1:
        if outputs and isinstance(outputs[0], dict):
            return [outputs]
        if outputs and isinstance(outputs[0], list):
            return outputs
        return None

    if outputs and isinstance(outputs[0], list) and len(outputs) == expected_count:
        return outputs

    if outputs and isinstance(outputs[0], dict):
        if len(outputs) == expected_count:
            return [[item] for item in outputs]
        if len(outputs) % expected_count == 0:
            group_size = len(outputs) // expected_count
            if group_size >= 2:
                return [
                    outputs[i * group_size:(i + 1) * group_size]
                    for i in range(expected_count)
                ]
    return None


def _batch_error_item(text: Any, language: str, model_name: str, message: str) -> Dict[str, Any]:
    """عنصر خطأ موحّد لصف فشل في predict_batch."""
    return {
        "text": text,
        "language": language,
        "cleaned_text": "",
        "sentiment": "neutral",
        "confidence": 0.0,
        "distribution": {},
        "is_reliable": False,
        "error": message,
        "model": model_name,
    }


def _merge_sentiment_scores(
    primary: List[Dict[str, Any]],
    secondary: List[Dict[str, Any]],
    secondary_weight: float = 0.45,
) -> List[Dict[str, Any]]:
    """
    دمج درجات نموذجين — للعربي: XLM-RoBERTa (55%) + CAMeLBERT (45%).

    يحسّن دقة اللهجات العربية مقارنة بنموذج واحد.
    """
    weights = {label: 0.0 for label in ["negative", "neutral", "positive"]}
    primary_weight = 1.0 - secondary_weight
    for item in primary:
        label = _normalize_label(str(item.get("label", "")))
        if label in weights:
            weights[label] += primary_weight * float(item.get("score", 0.0))
    for item in secondary:
        label = _normalize_label(str(item.get("label", "")))
        if label in weights:
            weights[label] += secondary_weight * float(item.get("score", 0.0))
    total = sum(weights.values()) or 1.0
    return [{"label": label, "score": score / total} for label, score in weights.items()]


def _model_ready(model_id: str) -> bool:
    """التحقق من وجود أوزان النموذج محلياً (بدون تنزيل)."""
    try:
        from huggingface_hub import snapshot_download

        path = snapshot_download(repo_id=model_id, local_files_only=True)
        return any(
            name.endswith((".bin", ".safetensors", ".h5"))
            for name in os.listdir(path)
        )
    except Exception:
        return False


def _get_multi_pipeline():
    """تحميل XLM-RoBERTa متعدد اللغات (lazy singleton — يُنزّل من HuggingFace إن لزم)."""
    global _MULTI_PIPELINE
    if _MULTI_PIPELINE is None:
        if not BERT_AVAILABLE:
            raise BertNotAvailableError("Install transformers and torch: pip install -r requirements.txt")
        logger.info("Loading multilingual BERT model: %s", MULTI_MODEL)
        _MULTI_PIPELINE = pipeline(
            "sentiment-analysis",
            model=MULTI_MODEL,
            tokenizer=MULTI_MODEL,
            top_k=None,
            truncation=True,
        )
    return _MULTI_PIPELINE


def _get_en_pipeline():
    """تحميل Twitter-RoBERTa للإنجليزي (lazy singleton — يُنزّل من HuggingFace إن لزم)."""
    global _EN_PIPELINE
    if _EN_PIPELINE is None:
        if not BERT_AVAILABLE:
            raise BertNotAvailableError("Install transformers and torch: pip install -r requirements.txt")
        logger.info("Loading English BERT model: %s", EN_MODEL)
        _EN_PIPELINE = pipeline(
            "sentiment-analysis",
            model=EN_MODEL,
            tokenizer=EN_MODEL,
            top_k=None,
            truncation=True,
        )
    return _EN_PIPELINE


def _get_ar_pipeline():
    """تحميل CAMeLBERT للعربي (lazy singleton — يُنزّل من HuggingFace إن لزم)."""
    global _AR_PIPELINE
    if _AR_PIPELINE is None:
        if not BERT_AVAILABLE:
            raise BertNotAvailableError("Install transformers and torch: pip install -r requirements.txt")
        logger.info("Loading Arabic CAMeLBERT model: %s", AR_MODEL)
        _AR_PIPELINE = pipeline(
            "sentiment-analysis",
            model=AR_MODEL,
            tokenizer=AR_MODEL,
            top_k=None,
            truncation=True,
        )
    return _AR_PIPELINE


class BertSentimentPredictor:
    """
    مصنّف BERT/Transformer — الواجهة الرئيسية للتحليل.

    neutral_threshold: إذا أعلى score < العتبة → نصنّف neutral (حذر)
    """

    def __init__(self, neutral_threshold: float = 0.58, root_dir: str | None = None) -> None:
        if not BERT_AVAILABLE:
            raise BertNotAvailableError(
                "BERT dependencies missing. Run: pip install -r requirements.txt"
            )
        self.neutral_threshold = neutral_threshold
        self.root_dir = root_dir
        if finetuned_model_available(root_dir):
            self.model_name = "xlm-roberta-finetuned"
        else:
            self.model_name = "xlm-roberta-multilingual"
        self.config = None

    def _scores_to_result(
        self,
        text: str,
        language: str,
        scores: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        يحوّل مخرجات pipeline HuggingFace إلى dict موحّد (نفس شكل TF-IDF).

        distribution: نسب مئوية للفئات الثلاث
        is_reliable: confidence >= عتبة YAML (55%)
        """
        parsed = []
        for item in scores:
            label = _normalize_label(str(item.get("label", "")))
            score = float(item.get("score", 0.0))
            if label in {"positive", "negative", "neutral"}:
                parsed.append((label, score))

        distribution = {label: 0.0 for label in ["negative", "neutral", "positive"]}
        for label, score in parsed:
            distribution[label] = safe_percent(score * 100.0)

        if not parsed:
            best_label = "neutral"
            confidence = 0.0
        elif len(parsed) >= 3:
            best_label, best_score = max(parsed, key=lambda x: x[1])
            confidence = safe_percent(best_score * 100.0)
        else:
            # ── نموذج ثنائي الفئات: عتبة neutral_threshold ──
            best_label, best_score = max(parsed, key=lambda x: x[1])
            if best_score < self.neutral_threshold:
                best_label = "neutral"
                confidence = safe_percent((1.0 - best_score) * 100.0)
            else:
                confidence = safe_percent(best_score * 100.0)

        threshold = 55.0
        return {
            "text": text,
            "language": language,
            "cleaned_text": text,
            "sentiment": best_label,
            "confidence": confidence,
            "distribution": distribution,
            "is_reliable": confidence >= threshold,
            "confidence_threshold": threshold,
            "model": self.model_name,
        }

    def _resolve_batch_language(
        self,
        index: int,
        texts: List[str],
        languages: List[Optional[str]],
        auto_language: bool,
    ) -> str:
        """تحديد لغة صف في الدفعة."""
        lang = languages[index] if index < len(languages) else None
        if lang and not auto_language:
            return lang
        raw = str(texts[index] or "").strip()
        return lang or detect_language(raw) if raw else "en"

    def _apply_batch_chunk(
        self,
        pipe,
        texts: List[str],
        languages: List[Optional[str]],
        chunk_indices: List[int],
        chunk: List[str],
        results: List[Dict[str, Any]],
        auto_language: bool,
    ) -> None:
        """تطبيق pipeline على دفعة — مع fallback لتحليل فردي عند الفشل."""
        try:
            outputs = pipe(chunk)
        except Exception as exc:
            logger.warning("Batch inference failed, falling back to single-item mode: %s", exc)
            outputs = None

        split = _split_pipeline_outputs(outputs, len(chunk)) if outputs is not None else None
        if split is not None and len(split) == len(chunk):
            for idx, scores in zip(chunk_indices, split):
                lang = self._resolve_batch_language(idx, texts, languages, auto_language)
                results[idx] = self._scores_to_result(str(texts[idx]), lang, scores)
            return

        # ── fallback: تحليل كل نص على حدة ──
        for idx in chunk_indices:
            raw = str(texts[idx] or "").strip()
            lang = self._resolve_batch_language(idx, texts, languages, auto_language)
            try:
                out = pipe(raw)
                scores = out[0] if out and isinstance(out[0], list) else out
                if not isinstance(scores, list):
                    scores = []
                results[idx] = self._scores_to_result(raw, lang, scores)
            except Exception as exc:
                logger.warning("Single-item inference failed for index %s: %s", idx, exc)
                results[idx] = _batch_error_item(
                    texts[idx],
                    lang,
                    self.model_name,
                    f"Analysis failed: {exc}",
                )

    def _finalize_batch_results(
        self,
        results: List[Dict[str, Any]],
        texts: List[str],
        languages: List[Optional[str]],
    ) -> List[Dict[str, Any]]:
        """إكمال أي صف فارغ بعنصر خطأ موحّد."""
        finalized: List[Dict[str, Any]] = []
        for index, item in enumerate(results):
            if item.get("sentiment") and item.get("language") is not None:
                finalized.append(item)
                continue
            if item.get("error"):
                finalized.append(item)
                continue
            lang = self._resolve_batch_language(index, texts, languages, auto_language=True)
            finalized.append(
                _batch_error_item(
                    texts[index],
                    lang,
                    self.model_name,
                    "Analysis failed",
                )
            )
        return finalized

    def predict_with_confidence(self, text: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        تحليل تعليق واحد — نقطة الدخول الرئيسية من الواجهة.

        ترتيب اختيار النموذج:
          1) fine-tuned محلي
          2) عربي: دمج XLM-RoBERTa + CAMeLBERT
          3) XLM-RoBERTa متعدد اللغات
          4) إنجليزي: Twitter-RoBERTa
          5) عربي: CAMeLBERT وحده
        """
        if not text or not text.strip():
            raise ValueError("Text must not be empty.")

        lang = language or detect_language(text)
        raw = text.strip()

        try:
            if finetuned_model_available(self.root_dir):
                scores = _get_finetuned_pipeline(self.root_dir)(raw)[0]
            elif (
                lang in {"ar_fusha", "ar_shami"}
                and not _cloud_light_mode()
            ):
                try:
                    scores_multi = _get_multi_pipeline()(raw)[0]
                    scores_ar = _get_ar_pipeline()(raw)[0]
                    scores = _merge_sentiment_scores(scores_multi, scores_ar, secondary_weight=0.45)
                except Exception:
                    scores = _get_multi_pipeline()(raw)[0]
            else:
                scores = _get_multi_pipeline()(raw)[0]
        except BertNotAvailableError:
            raise
        except Exception as exc:
            try:
                if lang == "en":
                    scores = _get_en_pipeline()(raw)[0]
                else:
                    scores = _get_ar_pipeline()(raw)[0]
            except Exception as fallback_exc:
                raise BertNotAvailableError(str(exc)) from fallback_exc

        return self._scores_to_result(raw, lang, scores)

    def predict_batch(
        self,
        texts: List[str],
        languages: Optional[List[Optional[str]]] = None,
        auto_language: bool = True,
        batch_size: int = 16,
    ) -> List[Dict[str, Any]]:
        """
        تحليل دفعة — يستخدم fine-tuned أو multi-model حسب التوفر.

        batch_size: عدد النصوص لكل استدعاء pipeline
        """
        languages = languages or [None] * len(texts)
        if _cloud_light_mode():
            batch_size = min(batch_size, 4)

        # ── مسار 1: fine-tuned ──
        if finetuned_model_available(self.root_dir):
            pipe = _get_finetuned_pipeline(self.root_dir)
            results: List[Dict[str, Any]] = [{} for _ in texts]
            valid_indices: List[int] = []
            valid_texts: List[str] = []

            for index, text in enumerate(texts):
                raw = str(text or "").strip()
                if not raw:
                    results[index] = {
                        "text": text,
                        "language": languages[index] or "en",
                        "cleaned_text": "",
                        "sentiment": "neutral",
                        "confidence": 0.0,
                        "distribution": {},
                        "is_reliable": False,
                        "error": "Empty comment",
                        "model": self.model_name,
                    }
                else:
                    valid_indices.append(index)
                    valid_texts.append(raw)

            for start in range(0, len(valid_texts), batch_size):
                chunk = valid_texts[start:start + batch_size]
                chunk_indices = valid_indices[start:start + batch_size]
                self._apply_batch_chunk(
                    pipe,
                    texts,
                    languages,
                    chunk_indices,
                    chunk,
                    results,
                    auto_language,
                )
            return self._finalize_batch_results(results, texts, languages)

        # ── مسار 2: XLM-RoBERTa متعدد اللغات (يُنزّل تلقائياً على السحابة) ──
        try:
            pipe = _get_multi_pipeline()
            results: List[Dict[str, Any]] = [{} for _ in texts]
            valid_indices: List[int] = []
            valid_texts: List[str] = []

            for index, text in enumerate(texts):
                raw = str(text or "").strip()
                if not raw:
                    results[index] = {
                        "text": text,
                        "language": languages[index] or "en",
                        "cleaned_text": "",
                        "sentiment": "neutral",
                        "confidence": 0.0,
                        "distribution": {},
                        "is_reliable": False,
                        "error": "Empty comment",
                        "model": self.model_name,
                    }
                else:
                    valid_indices.append(index)
                    valid_texts.append(raw)

            for start in range(0, len(valid_texts), batch_size):
                chunk = valid_texts[start:start + batch_size]
                chunk_indices = valid_indices[start:start + batch_size]
                self._apply_batch_chunk(
                    pipe,
                    texts,
                    languages,
                    chunk_indices,
                    chunk,
                    results,
                    auto_language,
                )
            return self._finalize_batch_results(results, texts, languages)
        except BertNotAvailableError:
            pass

        # ── مسار 3: فصل إنجليزي/عربي ──
        results = [{} for _ in texts]
        en_indices: List[int] = []
        en_texts: List[str] = []
        ar_indices: List[int] = []
        ar_texts: List[str] = []

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
                    "model": self.model_name,
                }
                continue

            resolved = lang if lang and not auto_language else (lang or detect_language(raw))
            if resolved == "en":
                en_indices.append(index)
                en_texts.append(raw)
            else:
                ar_indices.append(index)
                ar_texts.append(raw)

        if en_texts:
            try:
                en_pipe = _get_en_pipeline()
                for start in range(0, len(en_texts), batch_size):
                    chunk = en_texts[start:start + batch_size]
                    chunk_indices = en_indices[start:start + batch_size]
                    self._apply_batch_chunk(
                        en_pipe,
                        texts,
                        languages,
                        chunk_indices,
                        chunk,
                        results,
                        auto_language=False,
                    )
            except BertNotAvailableError:
                logger.warning("English BERT unavailable for batch path.")

        if ar_texts:
            try:
                ar_pipe = _get_ar_pipeline()
                for start in range(0, len(ar_texts), batch_size):
                    chunk = ar_texts[start:start + batch_size]
                    chunk_indices = ar_indices[start:start + batch_size]
                    self._apply_batch_chunk(
                        ar_pipe,
                        texts,
                        languages,
                        chunk_indices,
                        chunk,
                        results,
                        auto_language,
                    )
            except BertNotAvailableError:
                logger.warning("Arabic BERT unavailable for batch path.")

        return self._finalize_batch_results(results, texts, languages)

    def predict_dataframe(
        self,
        df: "pd.DataFrame",
        text_col: str = "text",
        language_col: str | None = "language",
        auto_language: bool = True,
    ):
        """تحليل DataFrame — للسكربتات والتقييم."""
        import pandas as pd

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


def load_bert_predictor(neutral_threshold: float = 0.58, root_dir: str | None = None) -> BertSentimentPredictor:
    """مصنع BertSentimentPredictor — يُستدعى من registry.load_predictor."""
    return BertSentimentPredictor(neutral_threshold=neutral_threshold, root_dir=root_dir)
