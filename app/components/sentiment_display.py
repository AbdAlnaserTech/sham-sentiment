from typing import Any, Dict

import streamlit as st

from language import LANGUAGE_LABEL_AR, SENTIMENT_LABEL_AR, sentiment_color

SENTIMENT_ICONS = {
    "positive": "😊",
    "negative": "😞",
    "neutral": "😐",
}


def render_sentiment_result(result: Dict[str, Any], rtl: bool = False) -> None:
    sentiment = result["sentiment"]
    sentiment_ar = SENTIMENT_LABEL_AR.get(sentiment, sentiment)
    lang_label = LANGUAGE_LABEL_AR.get(result["language"], result["language"])
    color = sentiment_color(sentiment)
    icon = SENTIMENT_ICONS.get(sentiment, "💬")
    confidence = float(result["confidence"])
    threshold = float(result.get("confidence_threshold", 55.0))
    is_reliable = result.get("is_reliable", confidence >= threshold)
    direction = "rtl" if rtl else "ltr"

    reliability_html = (
        "<span style='color:#059669;'>✅ تصنيف موثوق</span>"
        if is_reliable
        else "<span style='color:#d97706;'>⚠️ ثقة منخفضة — يُفضّل مراجعة بشرية</span>"
    )

    st.markdown(
        f"""
        <div class="result-card" style="direction:{direction}; border-right: 5px solid {color};">
            <div class="result-badge" style="background:{color}18; color:{color}; border:1px solid {color}40;">
                {icon} {sentiment_ar}
                <span style="font-size:0.75rem; opacity:0.8;">({sentiment.upper()})</span>
            </div>
            <div class="result-meta">🌐 {lang_label}</div>
            <div style="display:flex; align-items:baseline; gap:12px; margin:12px 0;">
                <span class="confidence-ring" style="color:{color};">{confidence:.0f}%</span>
                <span class="result-meta">مستوى الثقة / Confidence</span>
            </div>
            <div style="background:#e2e8f0; border-radius:999px; height:8px; overflow:hidden; margin:8px 0 12px;">
                <div style="background:{color}; width:{min(max(confidence, 0), 100):.0f}%; height:100%; border-radius:999px;"></div>
            </div>
            <div class="result-meta">{reliability_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
