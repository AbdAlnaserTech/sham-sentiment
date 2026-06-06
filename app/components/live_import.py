"""UI for fetching live comments from YouTube, Google Play, and Reddit."""

from typing import Any, Callable, List, Optional

import pandas as pd
import streamlit as st

from data.comment_fetcher import (
    FetchDependencyError,
    FetchError,
    FetchedComment,
    fetch_comments,
)


SOURCE_LABELS = {
    "youtube": "YouTube — تعليقات فيديو",
    "google_play": "Google Play — مراجعات تطبيق",
    "reddit": "Reddit — تعليقات منشور",
}

SOURCE_PLACEHOLDERS = {
    "youtube": "https://www.youtube.com/watch?v=VIDEO_ID",
    "google_play": "com.whatsapp أو رابط Google Play",
    "reddit": "https://www.reddit.com/r/.../comments/.../",
}


def render_live_import_panel(
    *,
    max_batch_size: int,
    on_analyze: Callable[[List[str]], None],
) -> None:
    st.markdown(
        '<div class="section-card">'
        "<p style='margin:0;color:#64748b;'>"
        "اجلب تعليقات <strong>حقيقية</strong> من الإنترنت ثم حلّلها دفعة واحدة."
        "</p></div>",
        unsafe_allow_html=True,
    )

    st.caption(
        "⚠️ Facebook / Instagram / TikTok تحتاج API رسمي من الشركة — "
        "غير متوفرة هنا. استخدم YouTube أو Google Play أو Reddit، أو ارفع CSV."
    )

    source = st.selectbox(
        "المصدر",
        options=["youtube", "google_play", "reddit"],
        format_func=lambda key: SOURCE_LABELS[key],
    )

    url = st.text_input(
        "الرابط أو المعرّف",
        placeholder=SOURCE_PLACEHOLDERS[source],
        key="live_fetch_url",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        max_items = st.slider("الحد الأقصى", 20, max_batch_size, min(200, max_batch_size), step=10)
    with c2:
        play_lang = st.selectbox("لغة المراجعات (Play)", ["ar", "en"], index=0)
    with c3:
        play_country = st.selectbox("البلد (Play)", ["sa", "ae", "us", "gb"], index=0)

    fetch_btn = st.button("📥 جلب التعليقات", type="secondary", use_container_width=True)

    if fetch_btn:
        if not url.strip():
            st.warning("أدخل الرابط أو معرّف التطبيق.")
        else:
            try:
                with st.spinner("جاري جلب التعليقات من الإنترنت..."):
                    comments, resolved = fetch_comments(
                        url.strip(),
                        source=source,
                        max_items=max_items,
                        play_lang=play_lang,
                        play_country=play_country,
                    )
                st.session_state["fetched_comments"] = comments
                st.session_state["fetched_source"] = resolved
                st.success(f"✅ تم جلب {len(comments)} تعليق/مراجعة من {SOURCE_LABELS.get(resolved, resolved)}")
            except FetchDependencyError as exc:
                st.error(str(exc))
                st.code("pip install -r requirements_fetch.txt", language="bash")
            except FetchError as exc:
                st.error(str(exc))

    comments: Optional[List[FetchedComment]] = st.session_state.get("fetched_comments")
    if comments:
        preview = pd.DataFrame([item.to_dict() for item in comments[:15]])
        st.markdown(f"**معاينة** ({len(comments)} إجمالاً)")
        st.dataframe(
            preview[["text", "author", "likes", "source"]].rename(columns={
                "text": "التعليق",
                "author": "الكاتب",
                "likes": "إعجاب",
                "source": "المصدر",
            }),
            use_container_width=True,
            hide_index=True,
        )

        analyze_live = st.button("🔍 تحليل كل التعليقات المجلوبة", type="primary", use_container_width=True)
        if analyze_live:
            texts = [item.text for item in comments[:max_batch_size]]
            if len(comments) > max_batch_size:
                st.warning(f"تم اقتصار التحليل على أول {max_batch_size} تعليق.")
            on_analyze(texts)

        st.download_button(
            "⬇️ حفظ التعليقات الخام CSV",
            data=pd.DataFrame([item.to_dict() for item in comments]).to_csv(index=False).encode("utf-8-sig"),
            file_name=f"fetched_{st.session_state.get('fetched_source', 'comments')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
