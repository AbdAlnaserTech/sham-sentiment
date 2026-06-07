"""Professional dashboard with KPIs and charts."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from analytics.alerts import predict_trend_label
from db.repository import fetch_dashboard_stats, list_batches


def render_dashboard() -> None:
    stats = fetch_dashboard_stats()
    totals = stats["totals"]

    st.markdown("### لوحة التحكم")

    if int(totals.get("batches") or 0) == 0:
        st.info(
            "لا توجد تحليلات محفوظة بعد. "
            "جرّب «تعليق واحد» أو «مجموعة تعليقات» — أو زر **تحميل أمثلة الدفعة** من الشريط الجانبي."
        )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("الدفعات", int(totals.get("batches") or 0))
    c2.metric("التعليقات", int(totals.get("items") or 0))
    c3.metric("إيجابي", int(totals.get("positive") or 0))
    c4.metric("سلبي", int(totals.get("negative") or 0))
    c5.metric("متوسط الثقة", f"{float(totals.get('avg_confidence') or 0):.1f}%")

    if int(totals.get("items") or 0) > 0:
        trend = predict_trend_label(
            int(totals.get("positive") or 0),
            int(totals.get("negative") or 0),
            int(totals.get("neutral") or 0),
        )
        st.info(f"**الاتجاه العام:** {trend['label_ar']} — {trend['recommendation_ar']}")

    col_chart, col_alerts = st.columns([1.2, 1])

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

        recent = stats.get("recent_batches") or []
        if recent:
            line_df = pd.DataFrame(recent).sort_values("created_at")
            fig2 = px.line(
                line_df,
                x="created_at",
                y="negative_count",
                markers=True,
                title="تطور التعليقات السلبية (آخر الدفعات)",
            )
            fig2.update_layout(margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig2, use_container_width=True)

    with col_alerts:
        st.markdown("#### التنبيهات")
        unread = int(stats.get("unread_alerts") or 0)
        if unread:
            st.warning(f"{unread} تنبيه غير مقروء")
        alerts = stats.get("recent_alerts") or []
        if not alerts:
            st.caption("لا توجد تنبيهات بعد.")
        for alert in alerts:
            icon = {"critical": "🔴", "warning": "🟠", "info": "🔵"}.get(alert["severity"], "•")
            st.markdown(f"{icon} **{alert['title']}** — {alert['message']}")
            st.caption(alert["created_at"])

    st.markdown("#### آخر عمليات التحليل")
    batches = list_batches(limit=20)
    if batches:
        st.dataframe(
            pd.DataFrame(batches),
            use_container_width=True,
            hide_index=True,
        )
