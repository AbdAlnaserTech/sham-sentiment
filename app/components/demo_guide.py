"""Sidebar shortcuts and defense demo hints."""

from __future__ import annotations

import streamlit as st

from components.demo_samples import DEMO_COMMENTS, get_demo_batch_text


DEFENSE_STEPS = """
**قبل العرض (5 دقائق)**
- شغّل `run.bat` → http://localhost:8501
- سجّل: `admin` / `Admin@2026`
- اختر **BERT** من الشريط الجانبي

**1. تعليق واحد (~2 د)**
- زر «مثال شامي» من الشريط الجانبي
- تحليل → إيجابي + ثقة + LIME + سحابة كلمات

**2. مجموعة تعليقات (~2 د)**
- زر «تحميل أمثلة الدفعة»
- تحليل المجموعة → رسم + كلمات + تنبيه + PDF

**3. لوحة التحكم (~1 د)**
- KPIs + توزيع المشاعر

**4. جلب من الإنترنت (~2 د — اختياري)**
- YouTube → 30 تعليق → جلب → تحليل

**5. الخاتمة (~1 د)**
- تبويب «حول المشروع» → QR + GitHub

**حسابات للجنة**
| admin | Admin@2026 |
| viewer | Viewer@2026 |
"""


def render_defense_sidebar() -> None:
    """Quick demo helpers for graduation presentation."""
    if not st.session_state.get("auth_user"):
        return

    st.markdown("**عرض للجنة**")
    if st.button("تحميل أمثلة الدفعة", key="sidebar_demo_batch", use_container_width=True):
        st.session_state["batch_comments_text"] = get_demo_batch_text()
        st.session_state["demo_hint"] = "انتقل إلى «مجموعة تعليقات» → اضغط «تحليل المجموعة»."
        st.rerun()

    if st.button("مثال شامي (تعليق واحد)", key="sidebar_demo_shami", use_container_width=True):
        st.session_state["single_comment"] = DEMO_COMMENTS[0]["text"]
        st.session_state["demo_hint"] = "انتقل إلى «تعليق واحد» → اضغط «تحليل التعليق» (BERT)."
        st.rerun()

    hint = st.session_state.pop("demo_hint", None)
    if hint:
        st.success(hint)

    with st.expander("سينario المناقشة (10 دقائق)", expanded=False):
        st.markdown(DEFENSE_STEPS)
