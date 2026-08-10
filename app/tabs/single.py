"""
تبويب «تعليق واحد» — تحليل فردي + wordcloud + حفظ.
"""

import streamlit as st

from components.analytics_panel import render_single_comment_save
from components.app_header import render_empty_result_panel
from components.auth_panel import current_user
from components.charts import render_distribution_pie
from components.demo_samples import render_demo_picker
from components.sentiment_display import render_sentiment_result
from components.wordcloud import render_wordcloud
from language import is_arabic
from models.bert_predictor import BertNotAvailableError
from cloud_setup import is_cloud_runtime
from shared import MODEL_KIND, append_history, get_predictor, resolve_language


def render_single_tab(*, auto_lang: bool, lang_choice: str) -> None:
    """واجهة التبويب كاملة."""
    col_input, col_result = st.columns([1.1, 1.0], gap="large")

    with col_input:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        render_demo_picker(key_prefix="single", text_key="single_comment")
        comment = st.text_area(
            "اكتب التعليق",
            height=160,
            placeholder="مثال: الخدمة كتير منيح والتوصيل كان سريع",
            key="single_comment",
            label_visibility="collapsed",
        )
        analyze_one = st.button("تحليل التعليق", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if analyze_one:
            if not comment.strip():
                st.warning("الرجاء إدخال تعليق.")
            else:
                try:
                    if not st.session_state.get("bert_ready") and is_cloud_runtime():
                        st.warning("انتظر حتى يظهر «النموذج جاهز» أعلى الصفحة ثم حاول مجدداً.")
                    else:
                        with st.spinner("جاري التحليل..."):
                            lang = resolve_language(comment, auto_lang, lang_choice)
                            result = get_predictor().predict_with_confidence(comment, language=lang)
                        st.session_state["last_result"] = result
                        st.session_state["last_comment"] = comment
                        append_history(result)
                except FileNotFoundError:
                    st.error("تعذّر تشغيل النظام. أعد تشغيل التطبيق أو تواصل مع المسؤول.")
                except ValueError as exc:
                    st.error(str(exc))
                except BertNotAvailableError:
                    st.error(
                        "تعذّر تحميل نموذج BERT على السحابة. "
                        "انتظر 1–2 دقيقة (تحميل أول مرة) ثم اضغط «تحليل التعليق» مجدداً."
                    )
                except Exception as exc:
                    st.error(f"حدث خطأ أثناء التحليل: {exc}")

    with col_result:
        st.markdown("#### النتيجة")
        last = st.session_state.get("last_result")
        last_comment = st.session_state.get("last_comment", "")

        if last:
            render_sentiment_result(last, rtl=is_arabic(last_comment or last.get("text", "")))
            st.markdown("##### نسب التصنيف")
            render_distribution_pie(last["distribution"])
        else:
            render_empty_result_panel()

    last = st.session_state.get("last_result")
    last_comment = st.session_state.get("last_comment", "")

    if last and last_comment:
        st.divider()
        st.markdown("#### أبرز الكلمات")
        render_wordcloud(last["cleaned_text"] or last["text"])
        st.divider()
        user = current_user()
        render_single_comment_save(
            last,
            last_comment,
            user_id=user["id"] if user else None,
            model_kind=MODEL_KIND,
        )
