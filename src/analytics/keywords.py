"""Keyword extraction from analyzed comments."""

from __future__ import annotations

from collections import Counter
from typing import Dict, List

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

from language import AR_STOPWORDS, EN_STOPWORDS
from preprocessing import TextPreprocessor


def extract_keywords_by_sentiment(
    df: pd.DataFrame,
    *,
    top_n: int = 12,
    text_col: str = "text",
    sentiment_col: str = "sentiment",
) -> Dict[str, List[Dict[str, object]]]:
    if df.empty or text_col not in df.columns:
        return {}

    pre = TextPreprocessor(remove_stopwords=True)
    output: Dict[str, List[Dict[str, object]]] = {}
    stop_words = list(EN_STOPWORDS | AR_STOPWORDS)

    for sentiment in ("positive", "negative", "neutral"):
        subset = df[df[sentiment_col] == sentiment] if sentiment_col in df.columns else df
        if subset.empty:
            output[sentiment] = []
            continue

        cleaned = []
        for _, row in subset.iterrows():
            raw = str(row.get(text_col, "")).strip()
            if not raw:
                continue
            lang = str(row.get("language", "en"))
            cleaned.append(pre.preprocess(raw, language=lang).cleaned_text)

        if not cleaned:
            output[sentiment] = []
            continue

        vectorizer = CountVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            stop_words=stop_words,
            token_pattern=r"(?u)\b[\w\u0600-\u06FF]{2,}\b",
        )
        try:
            matrix = vectorizer.fit_transform(cleaned)
            counts = matrix.sum(axis=0).A1
            terms = vectorizer.get_feature_names_out()
            ranked = sorted(zip(terms, counts), key=lambda x: x[1], reverse=True)[:top_n]
            output[sentiment] = [{"term": term, "count": int(count)} for term, count in ranked]
        except ValueError:
            output[sentiment] = []

    return output


def top_topics_overall(df: pd.DataFrame, top_n: int = 15) -> List[Dict[str, object]]:
    keywords = extract_keywords_by_sentiment(df, top_n=top_n)
    counter: Counter[str] = Counter()
    for items in keywords.values():
        for item in items:
            counter[item["term"]] += int(item["count"])
    return [{"term": k, "count": v} for k, v in counter.most_common(top_n)]
