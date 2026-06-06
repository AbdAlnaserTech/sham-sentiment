from typing import Any, Callable, Dict, Optional, Tuple

import pandas as pd
import streamlit as st

from language import SENTIMENT_LABEL_AR, sentiment_color


def render_model_comparison_table(
    tfidf_result: Optional[Dict[str, Any]],
    bert_result: Optional[Dict[str, Any]],
) -> None:
    st.subheader("⚖️ مقارنة النماذج / Model Comparison")

    if not tfidf_result and not bert_result:
        st.info("فعّل «مقارنة النماذج» من الشريط الجانبي ثم حلّل تعليقاً.")
        return

    rows = []
    for name, result in [("TF-IDF (سريع)", tfidf_result), ("BERT (دقيق)", bert_result)]:
        if not result:
            rows.append({"النموذج": name, "المشاعر": "—", "الثقة %": "—", "موثوق": "—"})
            continue
        sentiment_ar = SENTIMENT_LABEL_AR.get(result["sentiment"], result["sentiment"])
        rows.append({
            "النموذج": name,
            "المشاعر": f"{sentiment_ar} ({result['sentiment']})",
            "الثقة %": f"{float(result['confidence']):.1f}",
            "موثوق": "✅" if result.get("is_reliable", True) else "⚠️",
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if tfidf_result and bert_result:
        if tfidf_result["sentiment"] == bert_result["sentiment"]:
            st.success("النموذجان متفقان على نفس التصنيف ✅")
        else:
            st.warning(
                f"اختلاف: TF-IDF → {SENTIMENT_LABEL_AR.get(tfidf_result['sentiment'], tfidf_result['sentiment'])} | "
                f"BERT → {SENTIMENT_LABEL_AR.get(bert_result['sentiment'], bert_result['sentiment'])}"
            )

    col1, col2 = st.columns(2)
    with col1:
        if tfidf_result:
            _render_mini_card("TF-IDF", tfidf_result)
    with col2:
        if bert_result:
            _render_mini_card("BERT", bert_result)


def _render_mini_card(title: str, result: Dict[str, Any]) -> None:
    sentiment = result["sentiment"]
    color = sentiment_color(sentiment)
    sentiment_ar = SENTIMENT_LABEL_AR.get(sentiment, sentiment)
    st.markdown(
        f"""
        <div class="compare-card" style="border-right: 4px solid {color};">
            <strong>{title}</strong><br>
            <span style="color:{color}; font-size:1.2rem; font-weight:700;">{sentiment_ar}</span><br>
            <small>الثقة: {float(result['confidence']):.1f}%</small>
        </div>
        """,
        unsafe_allow_html=True,
    )


def predict_both_models(
    get_predictor_fn: Callable,
    text: str,
    language: str,
    compare_enabled: bool,
    preferred_model: str = "tfidf",
) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]], Dict[str, Any]]:
    tfidf_result = get_predictor_fn("tfidf").predict_with_confidence(text, language=language)
    bert_result = None

    if compare_enabled:
        try:
            bert_result = get_predictor_fn("bert").predict_with_confidence(text, language=language)
        except Exception as exc:
            st.warning(f"BERT غير متاح: {exc}")

    if preferred_model == "bert" and bert_result:
        primary = bert_result
    else:
        primary = tfidf_result

    return tfidf_result, bert_result, primary
