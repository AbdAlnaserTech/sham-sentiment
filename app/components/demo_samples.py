from typing import List

import streamlit as st

DEMO_COMMENTS: List[dict] = [
    {"label": "شامي — إيجابي", "text": "الخدمة كتير منيح والتوصيل كان سريع"},
    {"label": "فصحى — سلبي", "text": "المنتج سيئ ولم يلبِّ توقعاتي على الإطلاق"},
    {"label": "فصحى — محايد", "text": "التجربة عادية، لا أكثر ولا أقل"},
    {"label": "English — Positive", "text": "I genuinely loved the product; it exceeded my expectations."},
    {"label": "English — Negative", "text": "Terrible experience with customer support."},
]

DEMO_BATCH_TEXT = "\n".join(item["text"] for item in DEMO_COMMENTS)


def render_demo_picker(key_prefix: str = "single", text_key: str = "single_comment") -> None:
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
    return DEMO_BATCH_TEXT
