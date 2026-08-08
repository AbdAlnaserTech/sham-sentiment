"""Keywords, topics, and export actions for batch results."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

from analytics.alerts import detect_batch_alerts
from db.repository import save_batch_analysis
from reports.export import export_excel_bytes, export_pdf_bytes

_SOURCE_LABELS = {
    "manual": "يدوي",
    "single": "تعليق واحد",
    "live:youtube": "YouTube",
    "live:google_play": "Google Play",
    "live:reddit": "Reddit",
}


def _format_source_label(source: str) -> str:
    if source in _SOURCE_LABELS:
        return _SOURCE_LABELS[source]
    if source.startswith("live:"):
        return _SOURCE_LABELS.get(source, source.replace("live:", ""))
    return source


def _persist_batch_save(
    *,
    raw_results: List[Dict[str, Any]],
    user_id: Optional[int],
    model_kind: str,
    source: str,
    title: str,
    button_key: str,
) -> None:
    save_msg = st.session_state.get("batch_save_msg")
    if save_msg:
        st.success(save_msg)

    if st.button("حفظ في قاعدة البيانات", use_container_width=True, key=button_key):
        alerts = detect_batch_alerts(raw_results)
        batch_id = save_batch_analysis(
            user_id=user_id,
            title=title,
            source=source,
            model_kind=model_kind,
            results=raw_results,
            alerts=alerts,
        )
        st.session_state["batch_save_msg"] = f"تم الحفظ — رقم الدفعة #{batch_id}"
        st.rerun()


def render_single_comment_save(
    result: Dict[str, Any],
    comment: str,
    *,
    user_id: Optional[int],
    model_kind: str,
) -> None:
    payload = [{**result, "text": comment}]
    _persist_batch_save(
        raw_results=payload,
        user_id=user_id,
        model_kind=model_kind,
        source="single",
        title="تعليق واحد",
        button_key="save_single_comment_db",
    )


def render_batch_analytics(
    out_df: pd.DataFrame,
    raw_results: List[Dict[str, Any]],
    *,
    user_id: Optional[int],
    model_kind: str,
    source: str = "manual",
    title: str = "تحليل مجموعة",
    save_button_key: str = "save_batch_analytics_db",
) -> None:
    if out_df.empty:
        return

    st.markdown("#### تصدير التقرير")
    meta = {
        "المنصة": "تحليل آراء العملاء",
        "المصدر": _format_source_label(source) if source else "—",
        "العدد": len(out_df),
    }
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            "Excel",
            data=export_excel_bytes(out_df),
            file_name="تقرير_التعليقات.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with c2:
        try:
            pdf_bytes = export_pdf_bytes(out_df, title="تقرير تحليل التعليقات", meta=meta)
            st.download_button(
                "PDF",
                data=pdf_bytes,
                file_name="تقرير_التعليقات.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as exc:
            st.caption(f"تعذّر إنشاء PDF: {exc}")
    with c3:
        _persist_batch_save(
            raw_results=raw_results,
            user_id=user_id,
            model_kind=model_kind,
            source=source,
            title=title,
            button_key=save_button_key,
        )
