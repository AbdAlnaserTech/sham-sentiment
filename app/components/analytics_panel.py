"""Keywords, topics, and export actions for batch results."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

from analytics.alerts import detect_batch_alerts, predict_trend_label
from analytics.keywords import extract_keywords_by_sentiment, top_topics_overall
from db.repository import save_batch_analysis
from reports.export import export_excel_bytes, export_pdf_bytes


def render_batch_analytics(
    out_df: pd.DataFrame,
    raw_results: List[Dict[str, Any]],
    *,
    user_id: Optional[int],
    model_kind: str,
    source: str = "manual",
    title: str = "Batch Analysis",
) -> None:
    if out_df.empty:
        return

    st.markdown("#### تحليل متقدم")

    alerts = detect_batch_alerts(raw_results)
    for alert in alerts:
        if alert["severity"] == "critical":
            st.error(alert["message"])
        elif alert["severity"] == "warning":
            st.warning(alert["message"])
        else:
            st.info(alert["message"])

    valid = out_df[out_df["error"].astype(str) == ""] if "error" in out_df.columns else out_df
    if not valid.empty:
        trend = predict_trend_label(
            int((valid["sentiment"] == "positive").sum()),
            int((valid["sentiment"] == "negative").sum()),
            int((valid["sentiment"] == "neutral").sum()),
        )
        st.success(f"التوقع: {trend['label_ar']} — {trend['recommendation_ar']}")

    keywords = extract_keywords_by_sentiment(valid if not valid.empty else out_df)
    topics = top_topics_overall(valid if not valid.empty else out_df)

    k1, k2, k3 = st.columns(3)
    for col, label, key in [(k1, "إيجابي", "positive"), (k2, "سلبي", "negative"), (k3, "محايد", "neutral")]:
        with col:
            st.markdown(f"**كلمات {label}**")
            items = keywords.get(key, [])
            if items:
                st.write(", ".join(f"{i['term']} ({i['count']})" for i in items[:8]))
            else:
                st.caption("—")

    if topics:
        st.markdown("**أكثر المواضيع تكراراً:** " + ", ".join(t["term"] for t in topics[:10]))

    st.markdown("#### تصدير تقرير")
    meta = {
        "Model": model_kind,
        "Source": source,
        "Total": len(out_df),
    }
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            "Excel (.xlsx)",
            data=export_excel_bytes(out_df),
            file_name="sentiment_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with c2:
        try:
            pdf_bytes = export_pdf_bytes(out_df, title="Sentiment Analysis Report", meta=meta)
            st.download_button(
                "PDF",
                data=pdf_bytes,
                file_name="sentiment_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as exc:
            st.caption(f"تعذّر إنشاء PDF: {exc}")
    with c3:
        if st.button("حفظ في قاعدة البيانات", use_container_width=True):
            batch_id = save_batch_analysis(
                user_id=user_id,
                title=title,
                source=source,
                model_kind=model_kind,
                results=raw_results,
                alerts=alerts,
            )
            st.success(f"تم الحفظ — رقم الدفعة #{batch_id}")
