import re

ARABIC_LETTERS_RE = re.compile(
    r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]"
)

EN_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "he",
    "in", "is", "it", "its", "of", "on", "that", "the", "to", "was", "were", "will", "with",
}

AR_STOPWORDS = {
    "في", "على", "من", "الى", "إلى", "عن", "هذا", "هذه", "ذلك", "تلك", "هناك", "كما",
    "قد", "لم", "لن", "لا", "ما", "هو", "هي", "هم", "هن", "انا", "أنت", "انت", "نحن",
    "كان", "كانت", "يكون", "تكون", "ب", "و", "ثم",
}

SHAMI_HINT_WORDS = {
    "كتير", "كتيرر", "هلق", "لسا", "مو", "منيح", "تمام", "بدي", "بدّي", "شو", "ليش",
    "هيك", "هاد", "هاي", "عم", "رح", "مشان", "يعني",
}

SENTIMENT_LABEL_AR = {
    "positive": "إيجابي",
    "negative": "سلبي",
    "neutral": "محايد",
}

LANGUAGE_LABEL_AR = {
    "en": "English",
    "ar_fusha": "العربية الفصحى",
    "ar_shami": "العربية الشامية",
}


def is_arabic(text: str) -> bool:
    return bool(ARABIC_LETTERS_RE.search(text or ""))


def normalize_arabic(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r"[إأآا]", "ا", text)
    text = re.sub(r"ى", "ي", text)
    text = re.sub(r"ؤ", "و", text)
    text = re.sub(r"ئ", "ي", text)
    text = re.sub(r"ة", "ه", text)
    text = re.sub(r"ـ", "", text)
    text = re.sub(r"[\u064B-\u0652]", "", text)
    return text


def detect_language(text: str) -> str:
    if not text:
        return "en"

    if is_arabic(text):
        normalized = normalize_arabic(text)
        tokens = re.findall(r"[\u0600-\u06FF]+", normalized)
        if any(token in SHAMI_HINT_WORDS for token in tokens):
            return "ar_shami"
        return "ar_fusha"

    return "en"


def safe_percent(value: float) -> float:
    value = float(value)
    if value < 0:
        return 0.0
    if value > 100:
        return 100.0
    return value


def sentiment_color(sentiment: str) -> str:
    if sentiment == "positive":
        return "#16a34a"
    if sentiment == "negative":
        return "#dc2626"
    return "#ca8a04"
