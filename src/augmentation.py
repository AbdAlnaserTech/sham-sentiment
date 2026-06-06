import random
import re
from dataclasses import dataclass
from typing import Dict, Optional


_SENTIMENT_TO_EMOJIS = {
    "positive": ["😊", "😍", "😁", "😄", "✨", "🔥"],
    "negative": ["😤", "😡", "😠", "😞", "💔", "🙄"],
    "neutral": ["😐", "😶", "🤷", "🫤"],
}


_EN_HASHTAGS = {
    "positive": ["#loveit", "#happy", "#worthit", "#10of10"],
    "negative": ["#fail", "#disappointed", "#waste", "#neveragain"],
    "neutral": ["#update", "#fyi", "#thoughts"],
}

_AR_HASHTAGS = {
    "positive": ["#ممتاز", "#تجربه_رائعه", "#انصح_به"],
    "negative": ["#سيئ", "#تجربه_سيئه", "#لا_انصح"],
    "neutral": ["#ملاحظه", "#تحديث", "#رأي"],
}

_EN_MENTIONS = ["@support", "@brand", "@company"]
_AR_MENTIONS = ["@الدعم", "@الشركة", "@المتجر"]


_EN_SYNONYMS = {
    "great": ["excellent", "amazing", "solid"],
    "awesome": ["amazing", "fantastic"],
    "bad": ["poor", "terrible"],
    "frustrating": ["annoying", "irritating"],
    "loved": ["really liked", "enjoyed"],
    "hate": ["dislike"],
}

_AR_SYNONYMS = {
    "ممتاز": ["رائع", "جميل"],
    "سيئ": ["رديء", "غير جيد"],
    "مزعج": ["مضايق", "مؤذي"],
    "كتير": ["جدا", "بزيادة"],
    "منيح": ["تمام", "كويس"],
}


_ELONGATE_RE = re.compile(r"(.)\1{2,}")


def _maybe(prob: float) -> bool:
    return random.random() < prob


def add_social_flavor(text: str, sentiment: str, language: str) -> str:
    if not text:
        return text

    parts = [text]

    if language == "en":
        if _maybe(0.25):
            parts.append(random.choice(_EN_HASHTAGS[sentiment]))
        if _maybe(0.18):
            parts.append(random.choice(_EN_MENTIONS))
        if _maybe(0.10):
            parts.append("https://t.co/xyz")
    else:
        if _maybe(0.25):
            parts.append(random.choice(_AR_HASHTAGS[sentiment]))
        if _maybe(0.18):
            parts.append(random.choice(_AR_MENTIONS))
        if _maybe(0.10):
            parts.append("https://t.co/xyz")

    if _maybe(0.40):
        parts.append(random.choice(_SENTIMENT_TO_EMOJIS[sentiment]))

    if _maybe(0.15):
        parts.append(random.choice(["!", "!!", "...", "؟؟", "!!!"]))

    return " ".join(parts)


def synonym_replace(text: str, language: str, prob: float = 0.20) -> str:
    if not text or prob <= 0:
        return text

    mapping = _EN_SYNONYMS if language == "en" else _AR_SYNONYMS
    tokens = text.split()
    out = []
    for tok in tokens:
        key = tok.strip("،.!?؛:")
        if key in mapping and _maybe(prob):
            repl = random.choice(mapping[key])
            out.append(tok.replace(key, repl))
        else:
            out.append(tok)
    return " ".join(out)


def normalize_elongation(text: str) -> str:
    if not text:
        return text
    return _ELONGATE_RE.sub(r"\1\1", text)


@dataclass
class OptionalAugmenters:
    use_nlpaug: bool = False
    use_nlpaug_contextual: bool = False
    use_transformers: bool = False
    transformers_model_en: str = "Vamsi/T5_Paraphrase_Paws"
    nlpaug_contextual_model: str = "bert-base-multilingual-cased"


class Paraphraser:
    def __init__(self, cfg: OptionalAugmenters) -> None:
        self.cfg = cfg
        self._nlpaug_aug = None
        self._nlpaug_ctx_aug = None
        self._hf_pipe = None

        if cfg.use_nlpaug:
            try:
                import nlpaug.augmenter.word as naw

                self._nlpaug_aug = naw.SynonymAug(aug_src="wordnet")
            except Exception:
                self._nlpaug_aug = None

            if cfg.use_nlpaug_contextual:
                try:
                    import nlpaug.augmenter.word as naw

                    self._nlpaug_ctx_aug = naw.ContextualWordEmbsAug(
                        model_path=cfg.nlpaug_contextual_model,
                        action="substitute",
                    )
                except Exception:
                    self._nlpaug_ctx_aug = None

        if cfg.use_transformers:
            try:
                from transformers import pipeline

                self._hf_pipe = pipeline(
                    "text2text-generation",
                    model=cfg.transformers_model_en,
                )
            except Exception:
                self._hf_pipe = None

    def paraphrase(self, text: str, language: str) -> str:
        if not text:
            return text

        if language != "en":
            if self._nlpaug_ctx_aug is not None:
                try:
                    aug = self._nlpaug_ctx_aug.augment(text)
                    if isinstance(aug, list) and aug:
                        return str(aug[0])
                    if isinstance(aug, str) and aug:
                        return aug
                except Exception:
                    return text
            return text

        if self._hf_pipe is not None:
            try:
                out = self._hf_pipe(
                    f"paraphrase: {text}",
                    max_new_tokens=64,
                    do_sample=True,
                    top_p=0.9,
                    temperature=0.9,
                )
                if out and isinstance(out, list) and "generated_text" in out[0]:
                    return str(out[0]["generated_text"]).strip() or text
            except Exception:
                return text

        if self._nlpaug_aug is not None:
            try:
                aug = self._nlpaug_aug.augment(text)
                if isinstance(aug, list) and aug:
                    return str(aug[0])
                if isinstance(aug, str) and aug:
                    return aug
            except Exception:
                return text

        return text
