"""
تبويب «جلب من الإنترنت» — YouTube و Google Play.
"""

from typing import Callable, List, Optional

import pandas as pd
import streamlit as st

from data.comment_fetcher import (
    FetchDependencyError,
    FetchError,
    FetchedComment,
    fetch_comments,
)
from tabs.batch_helpers import execute_batch_analysis, render_batch_results_view

# ── بلوك 1: تسميات ونصوص مساعدة لكل مصدر ─────────────────────────────────
SOURCE_LABELS = {
    "youtube": "YouTube — تعليقات فيديو",
    "google_play": "Google Play — مراجعات تطبيق",
}

SOURCE_PLACEHOLDERS = {
    "youtube": "https://www.youtube.com/watch?v=VIDEO_ID",
    "google_play": "com.whatsapp أو رابط Google Play",
}

SOURCE_HINTS = {
    "youtube": "الصق رابط فيديو YouTube عاماً (ليس Shorts محذوفاً).",
    "google_play": "أدخل package id مثل com.whatsapp أو رابط التطبيق من Google Play.",
}


def render_live_import_panel(
    *,
    max_batch_size: int,
    on_analyze: Callable[[List[str]], None],
) -> None:
    """
    يبني واجهة الجلب والتحليل من مصادر خارجية.

    Args:
        max_batch_size: الحد الأقصى للتعليقات (من cloud_max_batch_size)
        on_analyze: callback من main.py → _execute_batch_analysis

    session_state:
      - fetched_comments → قائمة FetchedComment بعد الجلب
      - fetched_source → youtube | google_play
    """
    st.markdown(
        '<div class="section-card">'
        "<p style='margin:0;color:#64748b;'>"
        "اجلب تعليقات من الإنترنت ثم حلّلها دفعة واحدة."
        "</p></div>",
        unsafe_allow_html=True,
    )

    st.caption("المصادر المدعومة: YouTube · Google Play — أو ارفع ملف CSV من تبويب «مجموعة تعليقات».")

    source = st.selectbox(
        "المصدر",
        options=["youtube", "google_play"],
        format_func=lambda key: SOURCE_LABELS[key],
    )

    url = st.text_input(
        "الرابط أو المعرّف",
        placeholder=SOURCE_PLACEHOLDERS[source],
        key="live_fetch_url",
    )
    st.caption(SOURCE_HINTS[source])

    # ── إعدادات Google Play: اللغة والبلد ──
    if source == "google_play":
        c1, c2, c3 = st.columns(3)
        with c1:
            max_items = st.slider("عدد التعليقات", 20, max_batch_size, min(30, max_batch_size), step=10)
        with c2:
            play_lang = st.selectbox("لغة المراجعات", ["ar", "en"], index=0)
        with c3:
            play_country = st.selectbox("البلد", ["sa", "ae", "us", "gb"], index=0)
    else:
        max_items = st.slider("عدد التعليقات", 20, max_batch_size, min(30, max_batch_size), step=10)
        play_lang = "ar"
        play_country = "sa"

    fetch_btn = st.button("جلب التعليقات", type="secondary", use_container_width=True)

    # ── تنفيذ الجلب ──
    if fetch_btn:
        if not url.strip():
            st.warning("أدخل الرابط أو معرّف التطبيق.")
        else:
            try:
                with st.spinner("جاري جلب التعليقات..."):
                    comments, resolved = fetch_comments(
                        url.strip(),
                        source=source,
                        max_items=max_items,
                        play_lang=play_lang,
                        play_country=play_country,
                    )
                st.session_state["fetched_comments"] = comments
                st.session_state["fetched_source"] = resolved
                st.success(f"تم جلب {len(comments)} تعليق من {SOURCE_LABELS.get(resolved, resolved)}")
            except FetchDependencyError:
                st.error("تعذّر الاتصال بالمصدر. تأكد من تثبيت متطلبات الجلب ثم أعد تشغيل التطبيق.")
            except FetchError as exc:
                st.error(str(exc))

    # ── معاينة + تحليل + تصدير CSV ──
    comments: Optional[List[FetchedComment]] = st.session_state.get("fetched_comments")
    if comments:
        preview = pd.DataFrame([item.to_dict() for item in comments[:15]])
        st.markdown(f"**معاينة** ({len(comments)} إجمالاً)")
        st.dataframe(
            preview[["text", "author", "likes"]].rename(columns={
                "text": "التعليق",
                "author": "الكاتب",
                "likes": "إعجاب",
            }),
            use_container_width=True,
            hide_index=True,
        )

        analyze_live = st.button("تحليل التعليقات المجلوبة", type="primary", use_container_width=True)
        if analyze_live:
            texts = [item.text for item in comments[:max_batch_size]]
            if len(comments) > max_batch_size:
                st.warning(f"تم اقتصار التحليل على أول {max_batch_size} تعليق.")
            source_name = st.session_state.get("fetched_source", source)
            st.session_state["batch_source"] = f"live:{source_name}"
            label = SOURCE_LABELS.get(source_name, source_name)
            st.session_state["batch_title"] = f"جلب من الإنترنت — {label} ({len(texts)} تعليق)"
            on_analyze(texts)

        st.download_button(
            "تحميل التعليقات CSV",
            data=pd.DataFrame([item.to_dict() for item in comments]).to_csv(index=False).encode("utf-8-sig"),
            file_name="تعليقات_مجلوبة.csv",
            mime="text/csv",
            use_container_width=True,
        )


def render_live_tab(
    *,
    max_batch_size: int,
    auto_lang: bool,
    lang_choice: str,
) -> None:
    """تبويب كامل: جلب + تحليل + عرض النتائج."""
    render_live_import_panel(
        max_batch_size=max_batch_size,
        on_analyze=lambda texts: execute_batch_analysis(
            texts, auto_lang=auto_lang, lang_choice=lang_choice
        ),
    )
    if st.session_state.get("batch_results") is not None and str(
        st.session_state.get("batch_source", "")
    ).startswith("live:"):
        st.divider()
        st.markdown("#### نتائج التحليل")
        render_batch_results_view(save_button_key="save_live_tab")
