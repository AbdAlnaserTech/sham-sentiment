"""Sidebar shortcuts and defense demo hints."""

from __future__ import annotations

import streamlit as st

from components.demo_samples import DEMO_COMMENTS, get_demo_batch_text


def render_defense_sidebar() -> None:
    """Quick demo helpers for graduation presentation."""
    if not st.session_state.get("auth_user"):
        return

    st.markdown("**عرض للجنة**")
    if st.button("تحميل أمثلة الدفعة", key="sidebar_demo_batch", use_container_width=True):
        st.session_state["batch_comments_text"] = get_demo_batch_text()
        st.session_state["demo_hint"] = "انتقل إلى تبويب «مجموعة تعليقات» ثم اضغط «تحليل المجموعة»."
        st.rerun()

    if st.button("مثال شامي (تعليق واحد)", key="sidebar_demo_shami", use_container_width=True):
        st.session_state["single_comment"] = DEMO_COMMENTS[0]["text"]
        st.session_state["demo_hint"] = "انتقل إلى «تعليق واحد» واضغط «تحليل التعليق» (اختر BERT)."
        st.rerun()

    hint = st.session_state.pop("demo_hint", None)
    if hint:
        st.success(hint)

    with st.expander("خطوات العرض (3 دقائق)"):
        st.markdown(
            """
            1. **تعليق واحد** — BERT → ثقة + LIME
            2. **مجموعة** — كلمات مفتاحية + PDF
            3. **حول المشروع** — QR + GitHub
            """
        )
