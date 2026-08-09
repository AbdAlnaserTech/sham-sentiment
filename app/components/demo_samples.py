"""
أمثلة جاهزة للتجربة — تعليق واحد أو دفعة.

يُستدعى من:
  - تبويب «تعليق واحد» → render_demo_picker
  - تبويب «مجموعة تعليقات» → get_demo_batch_text (زر «تحميل أمثلة»)
"""

from typing import List

import streamlit as st

# ── بلوك: تعليقات تجريبية متنوعة (شامي، فصحى، إنجليزي) ───────────────────
DEMO_COMMENTS: List[dict] = [
    {"label": "شامي — إيجابي", "text": "الخدمة كتير منيح والتوصيل كان سريع"},
    {"label": "فصحى — سلبي", "text": "المنتج سيئ ولم يلبِّ توقعاتي على الإطلاق"},
    {"label": "فصحى — محايد", "text": "التجربة عادية، لا أكثر ولا أقل"},
    {"label": "إنجليزي — إيجابي", "text": "I genuinely loved the product; it exceeded my expectations."},
    {"label": "إنجليزي — سلبي", "text": "Terrible experience with customer support."},
]

# نص multiline جاهز للصق في تبويب «مجموعة تعليقات»
DEMO_BATCH_TEXT = "\n".join(item["text"] for item in DEMO_COMMENTS)


def render_demo_picker(key_prefix: str = "single", text_key: str = "single_comment") -> None:
    """
    لوحة أزرار لاختيار مثال جاهز — يملأ text_area عبر session_state.

    Args:
        key_prefix: بادئة مفاتيح الأزرار لتجنب التعارض
        text_key: مفتاح session_state لحقل النص (مثل single_comment)
    """
    st.markdown('<div class="demo-panel">', unsafe_allow_html=True)
    st.markdown("##### أمثلة جاهزة")
    row1 = st.columns(3)
    row2 = st.columns(2)

    for index, sample in enumerate(DEMO_COMMENTS):
        col = row1[index] if index < 3 else row2[index - 3]
        with col:
            if st.button(sample["label"], key=f"{key_prefix}_demo_{index}", use_container_width=True):
                st.session_state[text_key] = sample["text"]
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def get_demo_batch_text() -> str:
    """يرجع نص الدفعة التجريبية (سطر لكل تعليق)."""
    return DEMO_BATCH_TEXT
