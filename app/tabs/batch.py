"""
تبويب «مجموعة تعليقات» — لصق multiline أو رفع CSV.
"""

import streamlit as st

from components.batch_results import load_comments_from_upload, parse_comments_text
from components.demo_samples import get_demo_batch_text
from tabs.batch_helpers import execute_batch_analysis, render_batch_results_view


def render_batch_tab(*, max_batch_size: int, auto_lang: bool, lang_choice: str) -> None:
    """واجهة التبويب كاملة."""
    st.markdown(
        '<div class="section-card">'
        '<p style="margin:0;color:#64748b;">أدخل تعليقات — <strong>سطر لكل تعليق</strong> — أو ارفع ملف CSV</p>'
        "</div>",
        unsafe_allow_html=True,
    )

    btn_col, _ = st.columns([1, 2])
    with btn_col:
        if st.button("تحميل أمثلة", use_container_width=True):
            st.session_state["batch_comments_text"] = get_demo_batch_text()
            st.rerun()

    input_mode = st.radio(
        "طريقة الإدخال",
        options=["paste", "csv"],
        format_func=lambda x: "📝 لصق تعليقات" if x == "paste" else "📁 رفع CSV",
        horizontal=True,
        label_visibility="collapsed",
    )

    comments: list[str] = []

    if input_mode == "paste":
        raw = st.text_area(
            "التعليقات",
            height=200,
            placeholder="الخدمة ممتازة\nالتوصيل تأخر كثير\nThe app is okay",
            key="batch_comments_text",
            label_visibility="collapsed",
        )
        comments = parse_comments_text(raw)
        if raw.strip():
            st.caption(f"عدد التعليقات: **{len(comments)}** (الحد الأقصى {max_batch_size})")
            if len(comments) > max_batch_size:
                st.warning(f"تم اقتصار التحليل على أول {max_batch_size} تعليق.")
                comments = comments[:max_batch_size]
    else:
        uploaded = st.file_uploader("رفع ملف CSV", type=["csv"])
        if uploaded is not None:
            try:
                comments = load_comments_from_upload(uploaded)
                st.success(f"تم تحميل {len(comments)} تعليق.")
            except ValueError as exc:
                st.error(str(exc))

    if st.button("تحليل المجموعة", type="primary", use_container_width=True):
        st.session_state["batch_source"] = "manual"
        st.session_state["batch_title"] = f"تحليل يدوي ({len(comments)} تعليق)"
        execute_batch_analysis(comments, auto_lang=auto_lang, lang_choice=lang_choice)

    if st.session_state.get("batch_results") is not None and not str(
        st.session_state.get("batch_source", "")
    ).startswith("live:"):
        render_batch_results_view(save_button_key="save_batch_tab")
