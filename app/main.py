import bootstrap  # noqa: F401

import streamlit as st
from components.about_panel import render_about_panel
from components.analytics_panel import render_batch_analytics, render_single_comment_save
from components.app_header import (
    render_app_footer,
    render_app_header,
    render_sidebar_brand,
    render_empty_result_panel,
)
from components.auth_panel import can_admin, can_analyze, current_user, render_login_form
from components.dashboard_panel import render_dashboard
from components.batch_results import (
    append_batch_to_history,
    load_comments_from_upload,
    parse_comments_text,
    render_batch_results_table,
    render_batch_summary,
    run_batch_sentiment_analysis,
)
from components.charts import render_distribution_pie
from components.demo_samples import get_demo_batch_text, render_demo_picker
from components.live_import import render_live_import_panel
from components.sentiment_display import render_sentiment_result
from components.ui_styles import apply_app_styles
from components.wordcloud import render_wordcloud
from language import is_arabic
from shared import (
    append_history,
    get_predictor,
    init_app,
    render_sidebar_settings,
    resolve_language,
)
from cloud_setup import cloud_max_batch_size, is_cloud_runtime

st.set_page_config(
    page_title="تحليل آراء العملاء | جامعة الشام",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

paths, config = init_app()

if config.platform.get("require_login", True) and not render_login_form():
    with st.sidebar:
        render_sidebar_brand(config.ui)
    render_app_footer(config.ui)
    st.stop()

auto_lang, lang_choice, model_kind, rtl_mode, dark_mode = render_sidebar_settings(config.ui)
apply_app_styles(rtl_mode, dark_mode)

MAX_BATCH_SIZE = cloud_max_batch_size(int(config.inference.get("max_batch_size", 2000)))

if not can_analyze():
    render_app_header(config.ui)
    st.info("حساب **viewer** — لوحة التحكم و«حول المشروع» فقط (بدون تحليل).")
    tab_view_dash, tab_view_about = st.tabs(["لوحة التحكم", "حول المشروع"])
    with tab_view_dash:
        render_dashboard(can_manage_data=can_admin())
    with tab_view_about:
        render_about_panel(config)
    render_app_footer(config.ui)
    st.stop()

render_app_header(config.ui)


def _render_batch_results_view(*, save_button_key: str = "save_batch_tab") -> None:
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
        model_kind=model_kind,
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


def _execute_batch_analysis(comments: list[str]) -> None:
    if not comments:
        st.warning("أدخل تعليقاً واحداً على الأقل.")
        return
    try:
        predictor = get_predictor(model_kind)
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
        st.error(f"حدث خطأ أثناء تحليل الدفعة: {exc}")

tab_dashboard, tab_single, tab_batch, tab_live, tab_about = st.tabs([
    "لوحة التحكم",
    "تعليق واحد",
    "مجموعة تعليقات",
    "جلب من الإنترنت",
    "حول المشروع",
])

with tab_about:
    render_about_panel(config)

with tab_dashboard:
    render_dashboard(can_manage_data=can_admin())

with tab_single:
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
                    with st.spinner("جاري التحليل..."):
                        lang = resolve_language(comment, auto_lang, lang_choice)
                        result = get_predictor(model_kind).predict_with_confidence(comment, language=lang)
                    st.session_state["last_result"] = result
                    st.session_state["last_comment"] = comment
                    append_history(result)
                except FileNotFoundError:
                    st.error("تعذّر تشغيل النظام. أعد تشغيل التطبيق أو تواصل مع المسؤول.")
                except ValueError as exc:
                    st.error(str(exc))

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
            model_kind=model_kind,
        )

with tab_batch:
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
            st.caption(f"عدد التعليقات: **{len(comments)}** (الحد الأقصى {MAX_BATCH_SIZE})")
            if len(comments) > MAX_BATCH_SIZE:
                st.warning(f"تم اقتصار التحليل على أول {MAX_BATCH_SIZE} تعليق.")
                comments = comments[:MAX_BATCH_SIZE]
    else:
        uploaded = st.file_uploader("رفع ملف CSV", type=["csv"])
        if uploaded is not None:
            try:
                comments = load_comments_from_upload(uploaded)
                st.success(f"تم تحميل {len(comments)} تعليق.")
            except ValueError as exc:
                st.error(str(exc))

    analyze_many = st.button("تحليل المجموعة", type="primary", use_container_width=True)

    if analyze_many:
        st.session_state["batch_source"] = "manual"
        st.session_state["batch_title"] = f"تحليل يدوي ({len(comments)} تعليق)"
        _execute_batch_analysis(comments)

    if st.session_state.get("batch_results") is not None and not str(
        st.session_state.get("batch_source", "")
    ).startswith("live:"):
        _render_batch_results_view(save_button_key="save_batch_tab")

with tab_live:
    render_live_import_panel(
        max_batch_size=MAX_BATCH_SIZE,
        on_analyze=_execute_batch_analysis,
    )
    if st.session_state.get("batch_results") is not None and str(
        st.session_state.get("batch_source", "")
    ).startswith("live:"):
        st.divider()
        st.markdown("#### نتائج التحليل")
        _render_batch_results_view(save_button_key="save_live_tab")

render_app_footer(config.ui)
