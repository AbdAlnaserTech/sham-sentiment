from datetime import datetime, timezone
from typing import Any, Dict, List

import pandas as pd
import plotly.express as px
import streamlit as st

from language import SENTIMENT_LABEL_AR, detect_language


def parse_comments_text(raw: str) -> List[str]:
    lines = [line.strip() for line in raw.splitlines()]
    return [line for line in lines if line]


def results_to_dataframe(results: List[Dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for item in results:
        rows.append({
            "text": item.get("text", ""),
            "language": item.get("language", ""),
            "sentiment": item.get("sentiment", ""),
            "sentiment_ar": SENTIMENT_LABEL_AR.get(item.get("sentiment", ""), ""),
            "confidence": item.get("confidence", 0.0),
            "is_reliable": item.get("is_reliable", False),
            "error": item.get("error", ""),
        })
    return pd.DataFrame(rows)


def render_batch_summary(df: pd.DataFrame) -> None:
    if df.empty:
        return

    valid = df[df["error"].astype(str) == ""]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("المجموع / Total", len(df))
    c2.metric("إيجابي / Positive", int((valid["sentiment"] == "positive").sum()))
    c3.metric("سلبي / Negative", int((valid["sentiment"] == "negative").sum()))
    c4.metric("محايد / Neutral", int((valid["sentiment"] == "neutral").sum()))

    if valid.empty:
        return

    chart_df = valid["sentiment"].value_counts().reset_index()
    chart_df.columns = ["sentiment", "count"]
    chart_df["label"] = chart_df["sentiment"].map(
        lambda value: f"{SENTIMENT_LABEL_AR.get(value, value)} ({value})"
    )
    fig = px.bar(
        chart_df,
        x="label",
        y="count",
        color="sentiment",
        color_discrete_map={
            "positive": "#059669",
            "negative": "#dc2626",
            "neutral": "#d97706",
        },
        title="توزيع المشاعر / Sentiment Distribution",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=40, b=20, l=20, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)


def append_batch_to_history(results: List[Dict[str, Any]]) -> None:
    now = datetime.now(timezone.utc).isoformat()
    for item in results:
        if item.get("error"):
            continue
        sentiment = item.get("sentiment")
        text = item.get("text", "")
        if not sentiment:
            continue
        st.session_state["history"].append({
            "timestamp": now,
            "language": item.get("language") or detect_language(str(text)),
            "sentiment": sentiment,
            "confidence": item.get("confidence", 0.0),
            "is_reliable": item.get("is_reliable", True),
            "text": text,
        })


def load_comments_from_upload(uploaded_file) -> List[str]:
    df = pd.read_csv(uploaded_file)
    if "text" not in df.columns:
        raise ValueError("CSV must contain a `text` column.")
    return [str(value).strip() for value in df["text"].tolist() if str(value).strip()]


def run_batch_sentiment_analysis(
    comments: List[str],
    predictor,
    *,
    auto_lang: bool,
    lang_choice: str,
) -> tuple[pd.DataFrame, List[Dict[str, Any]]]:
    languages = None if auto_lang else [lang_choice] * len(comments)
    results = predictor.predict_batch(
        comments,
        languages=languages,
        auto_language=auto_lang,
    )
    return results_to_dataframe(results), results


def render_batch_results_table(out_df: pd.DataFrame) -> None:
    display_df = out_df[[
        "text", "sentiment_ar", "sentiment", "language", "confidence", "is_reliable", "error"
    ]].rename(columns={
        "text": "التعليق",
        "sentiment_ar": "المشاعر",
        "sentiment": "sentiment",
        "language": "اللغة",
        "confidence": "الثقة %",
        "is_reliable": "موثوق",
        "error": "خطأ",
    })
    st.dataframe(display_df, use_container_width=True, hide_index=True)
