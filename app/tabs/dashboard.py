"""
لوحة التحكم — KPIs، رسوم، تنبيهات، وإدارة البيانات المحفوظة.

يُستدعى من main.py في تبويب «لوحة التحكم».
يقرأ الإحصائيات من SQLite عبر db.repository و db.batch_ops.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from db.batch_ops import delete_all_saved_batches, delete_batch, fetch_all_saved_items
from db.repository import fetch_dashboard_stats, list_batches
from language import SENTIMENT_LABEL_AR
from reports.export import export_excel_bytes

# ── بلوك 1: تسميات مصدر الدفعة للعرض العربي ─────────────────────────────
_SOURCE_LABELS = {
    "manual": "يدوي",
    "single": "تعليق واحد",
    "live:youtube": "YouTube",
    "live:google_play": "Google Play",
    "live:reddit": "Reddit",
}


def _format_batch_source(source: str) -> str:
    """يحوّل مفتاح المصدر إلى تسمية عربية للجدول."""
    if source in _SOURCE_LABELS:
        return _SOURCE_LABELS[source]
    if source.startswith("live:"):
        return _SOURCE_LABELS.get(source, source.replace("live:", ""))
    return source


def _batches_display_df(batches: list) -> pd.DataFrame:
    """
    يحوّل قائمة الدفعات من DB إلى DataFrame بأعمدة عربية.

    يُستخدم في جدول «آخر عمليات التحليل».
    """
    df = pd.DataFrame(batches)
    if df.empty:
        return df
    display = df[[
        "id", "title", "source", "total_count", "positive_count",
        "negative_count", "neutral_count", "created_at",
    ]].rename(columns={
        "id": "الرقم",
        "title": "العنوان",
        "source": "المصدر",
        "total_count": "العدد",
        "positive_count": "إيجابي",
        "negative_count": "سلبي",
        "neutral_count": "محايد",
        "created_at": "التاريخ",
    })
    display["المصدر"] = df["source"].map(_format_batch_source)
    return display


def render_dashboard(*, can_manage_data: bool = False) -> None:
    """
    يبني لوحة التحكم الكاملة.

    Args:
        can_manage_data: True لحساب admin — يُفعّل حذف الدفعات
    """
    stats = fetch_dashboard_stats()
    totals = stats["totals"]

    st.markdown("### لوحة التحكم")

    if int(totals.get("batches") or 0) == 0:
        st.info(
            "لا توجد تحليلات محفوظة بعد. "
            "جرّب «تعليق واحد» أو «مجموعة تعليقات»."
        )

    # ── KPIs — الدفعات، التعليقات، المشاعر، متوسط اليقين ──
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("الدفعات", int(totals.get("batches") or 0))
    c2.metric("التعليقات", int(totals.get("items") or 0))
    c3.metric("إيجابي", int(totals.get("positive") or 0))
    c4.metric("سلبي", int(totals.get("negative") or 0))
    c5.metric("متوسط اليقين", f"{float(totals.get('avg_confidence') or 0):.1f}%")

    if int(totals.get("items") or 0) > 0:
        pos = int(totals.get("positive") or 0)
        neg = int(totals.get("negative") or 0)
        neu = int(totals.get("neutral") or 0)
        total = pos + neg + neu
        if total > 0:
            dominant = max((pos, "إيجابي"), (neg, "سلبي"), (neu, "محايد"), key=lambda x: x[0])
            pct = dominant[0] * 100 // total
            st.caption(f"**الصورة العامة:** {dominant[1]} ({pct}% من التعليقات المحفوظة)")

    col_chart, col_alerts = st.columns([1.2, 1])

    # ── رسم توزيع المشاعر الإجمالي ──
    with col_chart:
        pie_df = pd.DataFrame([
            {"sentiment": "positive", "count": totals.get("positive", 0), "label": "إيجابي"},
            {"sentiment": "negative", "count": totals.get("negative", 0), "label": "سلبي"},
            {"sentiment": "neutral", "count": totals.get("neutral", 0), "label": "محايد"},
        ])
        if pie_df["count"].sum() > 0:
            fig = px.pie(
                pie_df,
                names="label",
                values="count",
                color="sentiment",
                color_discrete_map={
                    "positive": "#059669",
                    "negative": "#dc2626",
                    "neutral": "#d97706",
                },
                title="توزيع المشاعر الإجمالي",
            )
            fig.update_layout(margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig, use_container_width=True)

    # ── التنبيهات الأخيرة من analytics.alerts ──
    with col_alerts:
        st.markdown("#### ملاحظات")
        unread = int(stats.get("unread_alerts") or 0)
        if unread:
            st.warning(f"{unread} ملاحظة جديدة")
        alerts = stats.get("recent_alerts") or []
        if not alerts:
            st.caption("لا توجد ملاحظات بعد.")
        for alert in alerts:
            icon = {"critical": "🔴", "warning": "🟠", "info": "🔵"}.get(alert["severity"], "•")
            st.markdown(f"{icon} **{alert['title']}** — {alert['message']}")
            st.caption(alert["created_at"])

    st.markdown("#### آخر عمليات التحليل")
    batches = list_batches(limit=20)
    if batches:
        st.dataframe(
            _batches_display_df(batches),
            use_container_width=True,
            hide_index=True,
        )

    # ── expander: تصدير احتياطي + حذف (admin فقط) ──
    if int(totals.get("items") or 0) > 0:
        with st.expander("إدارة البيانات المحفوظة", expanded=False):
            st.caption("صدّر نسخة احتياطية قبل أي حذف — الحذف نهائي.")
            all_items = fetch_all_saved_items()
            if not all_items.empty:
                export_df = all_items.copy()
                export_df["sentiment_ar"] = export_df["sentiment"].map(
                    lambda value: SENTIMENT_LABEL_AR.get(value, value)
                )
                export_df = export_df[[
                    "batch_id",
                    "batch_title",
                    "batch_source",
                    "batch_date",
                    "comment",
                    "language",
                    "sentiment_ar",
                    "confidence",
                    "is_reliable",
                    "error",
                    "analyzed_at",
                ]].rename(columns={
                    "batch_id": "رقم الدفعة",
                    "batch_title": "العنوان",
                    "batch_source": "المصدر",
                    "batch_date": "تاريخ الدفعة",
                    "comment": "التعليق",
                    "language": "اللغة",
                    "sentiment_ar": "المشاعر",
                    "confidence": "اليقين %",
                    "is_reliable": "موثوق",
                    "error": "خطأ",
                    "analyzed_at": "تاريخ التحليل",
                })
                export_df["المصدر"] = export_df["المصدر"].map(_format_batch_source)
                c1, c2 = st.columns(2)
                with c1:
                    st.download_button(
                        "تحميل CSV",
                        data=export_df.to_csv(index=False).encode("utf-8-sig"),
                        file_name="كل_التعليقات_المحفوظة.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="export_all_csv",
                    )
                with c2:
                    st.download_button(
                        "تحميل Excel",
                        data=export_excel_bytes(export_df, sheet_name="SavedComments"),
                        file_name="كل_التعليقات_المحفوظة.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key="export_all_xlsx",
                    )

            if can_manage_data and int(totals.get("batches") or 0) > 0:
                st.divider()
                st.markdown("**حذف (مدير النظام)**")
                batches = list_batches(limit=100)
                batch_labels = {
                    b["id"]: f"#{b['id']} — {b['title']} ({b['total_count']} تعليق)"
                    for b in batches
                }
                selected_id = st.selectbox(
                    "دفعة للحذف",
                    options=list(batch_labels.keys()),
                    format_func=lambda batch_id: batch_labels[batch_id],
                    key="delete_batch_select",
                )
                confirm_one = st.checkbox("أؤكد حذف الدفعة المحددة", key="confirm_delete_one")
                if st.button(
                    "حذف الدفعة",
                    use_container_width=True,
                    disabled=not confirm_one,
                    key="delete_one_batch",
                ):
                    if delete_batch(int(selected_id)):
                        st.session_state.pop("batch_save_msg", None)
                        st.success(f"تم حذف الدفعة #{selected_id}.")
                        st.rerun()
                    else:
                        st.error("تعذّر حذف الدفعة.")

                st.divider()
                confirm_all = st.checkbox("أؤكد حذف كل البيانات", key="confirm_delete_all")
                if st.button(
                    "حذف الكل",
                    use_container_width=True,
                    disabled=not confirm_all,
                    key="delete_all_batches",
                ):
                    deleted = delete_all_saved_batches()
                    st.session_state.pop("batch_results", None)
                    st.session_state.pop("batch_raw_results", None)
                    st.session_state.pop("batch_save_msg", None)
                    st.success(f"تم حذف {deleted} دفعة.")
                    st.rerun()
            elif int(totals.get("batches") or 0) > 0:
                st.caption("الحذف متاح لحساب مدير النظام فقط.")


# اسم موحّد مع باقي التبويبات
render_dashboard_tab = render_dashboard
