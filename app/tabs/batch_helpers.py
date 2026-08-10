"""
مساعد مشترك — تحليل وعرض نتائج الدفعات.

يُستخدم من:
  - tabs/batch.py   (لصق / CSV)
  - tabs/live.py    (YouTube / Google Play)
"""

from __future__ import annotations

import streamlit as st

from components.analytics_panel import render_batch_analytics
from components.auth_panel import current_user
from components.batch_results import (
    append_batch_to_history,
    render_batch_results_table,
    render_batch_summary,
    run_batch_sentiment_analysis,
)
from shared import MODEL_KIND, get_predictor

from cloud_setup import is_cloud_runtime


def render_batch_results_view(*, save_button_key: str) -> None:
    """ملخص + جدول + حفظ + تصدير CSV."""
    out_df = st.session_state.get("batch_results")
    results = st.session_state.get("batch_raw_results")
    if out_df is None:
        return

    render_batch_summary(out_df)
    render_batch_results_table(out_df)
    user = current_user()
    render_batch_analytics(
        out_df,
        results or [],
        user_id=user["id"] if user else None,
        model_kind=MODEL_KIND,
        source=st.session_state.get("batch_source", "manual"),
        title=st.session_state.get("batch_title", "تحليل مجموعة"),
        save_button_key=save_button_key,
    )
    st.download_button(
        "تصدير النتائج CSV",
        data=out_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="نتائج_التعليقات.csv",
        mime="text/csv",
        use_container_width=True,
        key=f"csv_{save_button_key}",
    )


def execute_batch_analysis(
    comments: list[str],
    *,
    auto_lang: bool,
    lang_choice: str,
) -> None:
    """تشغيل BERT على قائمة تعليقات."""
    if not comments:
        st.warning("أدخل تعليقاً واحداً على الأقل.")
        return
    try:
        if is_cloud_runtime() and not st.session_state.get("bert_ready"):
            st.warning("انتظر حتى يظهر «✅ النموذج جاهز» أعلى الصفحة.")
            return
        predictor = get_predictor()
        progress = st.progress(0, text=f"جاري تحليل {len(comments)} تعليق...")
        status = st.empty()
        out_df, results = run_batch_sentiment_analysis(
            comments,
            predictor,
            auto_lang=auto_lang,
            lang_choice=lang_choice,
            progress_bar=progress,
            status_text=status,
        )
        progress.empty()
        status.empty()
        st.session_state["batch_results"] = out_df
        st.session_state["batch_raw_results"] = results
        st.session_state.pop("batch_save_msg", None)
        append_batch_to_history(results)
        st.success(f"تم تحليل {len(out_df)} تعليق.")
    except FileNotFoundError:
        st.error("تعذّر تشغيل النظام. أعد تشغيل التطبيق أو تواصل مع المسؤول.")
    except Exception as exc:
        message = str(exc)
        if "BERT" in message or "transformers" in message or "torch" in message.lower():
            st.error(
                "تعذّر تحميل نموذج BERT. على Streamlit Cloud انتظر دقيقة ثم أعد المحاولة "
                "(أول تحليل يحمّل النموذج من HuggingFace)."
            )
        else:
            st.error(f"حدث خطأ أثناء تحليل الدفعة: {exc}")
