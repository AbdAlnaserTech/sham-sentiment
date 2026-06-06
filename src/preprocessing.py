import re
from dataclasses import dataclass
from typing import List, Optional

from language import AR_STOPWORDS, EN_STOPWORDS, detect_language, normalize_arabic


_PUNCT_NUM_RE = re.compile(r"[^\w\s\u0600-\u06FF#@]+", flags=re.UNICODE)
_MULTI_SPACE_RE = re.compile(r"\s+")
_ELONGATION_RE = re.compile(r"(.)\1{2,}")

_EMOJI_TO_TOKEN = {
    "😊": "emoji_pos", "😍": "emoji_pos", "😁": "emoji_pos", "😄": "emoji_pos", "🙂": "emoji_pos",
    "😤": "emoji_neg", "😡": "emoji_neg", "😠": "emoji_neg", "😞": "emoji_neg", "😢": "emoji_neg",
    "😐": "emoji_neu", "😶": "emoji_neu", "🙃": "emoji_neg",
}

_EMOTICON_TO_TOKEN = {
    ":)": "emoji_pos", ":-)": "emoji_pos", ":D": "emoji_pos",
    ":(": "emoji_neg", ":-(": "emoji_neg",
}


@dataclass
class PreprocessResult:
    cleaned_text: str
    tokens: List[str]
    language: str


class TextPreprocessor:
    def __init__(
        self,
        remove_stopwords: bool = True,
        min_token_len: int = 2,
        normalize_elongation: bool = True,
    ) -> None:
        self.remove_stopwords = remove_stopwords
        self.min_token_len = min_token_len
        self.normalize_elongation = normalize_elongation

    def preprocess(self, text: str | None, language: Optional[str] = None) -> PreprocessResult:
        text = text or ""
        lang = language or detect_language(text)
        cleaned = self._normalize_and_clean(text, lang)
        tokens = self._tokenize(cleaned)
        tokens = self._postprocess_tokens(tokens, lang)
        return PreprocessResult(cleaned_text=" ".join(tokens), tokens=tokens, language=lang)

    def _normalize_and_clean(self, text: str, lang: str) -> str:
        text = text.strip()

        for emo, token in _EMOTICON_TO_TOKEN.items():
            text = text.replace(emo, f" {token} ")
        for emo, token in _EMOJI_TO_TOKEN.items():
            text = text.replace(emo, f" {token} ")

        if lang == "en":
            text = text.lower()

        if lang in {"ar_fusha", "ar_shami"}:
            text = normalize_arabic(text)

        if self.normalize_elongation:
            text = _ELONGATION_RE.sub(r"\1\1", text)

        text = _PUNCT_NUM_RE.sub(" ", text)
        text = _MULTI_SPACE_RE.sub(" ", text)
        return text.strip()

    def _tokenize(self, text: str) -> List[str]:
        return text.split() if text else []

    def _postprocess_tokens(self, tokens: List[str], lang: str) -> List[str]:
        if self.min_token_len > 1:
            tokens = [token for token in tokens if len(token) >= self.min_token_len]

        if self.remove_stopwords:
            stopwords = EN_STOPWORDS if lang == "en" else AR_STOPWORDS
            tokens = [token for token in tokens if token not in stopwords]

        return tokens
