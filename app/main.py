import bootstrap  # noqa: F401

import json
import os

import streamlit as st
from components.about_panel import render_about_panel
from components.analytics_panel import render_batch_analytics
from components.app_header import render_app_footer, render_app_header, render_empty_result_panel
from components.auth_panel import can_analyze, current_user, render_login_form, render_user_menu
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
from components.explain_display import render_lime_explanation
from components.live_import import render_live_import_panel
from components.model_compare import predict_both_models, render_model_comparison_table
from components.sentiment_display import render_sentiment_result
from components.ui_styles import apply_app_styles
from components.wordcloud import render_wordcloud
from language import is_arabic
from paths import ProjectPaths, get_project_root
from shared import (
    append_history,
    get_predictor,
    init_app,
    render_sidebar_settings,
    resolve_language,
)
from cloud_setup import cloud_max_batch_size, is_cloud_runtime

st.set_page_config(
    page_title="تحليل المشاعر | جامعة الشام",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

paths, config = init_app()
auto_lang, lang_choice, model_kind, compare_models, rtl_mode, dark_mode = render_sidebar_settings(config.ui)
apply_app_styles(rtl_mode, dark_mode)

MAX_BATCH_SIZE = cloud_max_batch_size(int(config.inference.get("max_batch_size", 2000)))

if config.platform.get("require_login", True) and not render_login_form():
    render_app_footer(config.ui)
    st.stop()

render_user_menu()

if not can_analyze():
    render_app_header(config.ui)
    st.info("حساب **viewer** — لوحة التحكم و«حول المشروع» فقط (بدون تحليل).")
    tab_view_dash, tab_view_about = st.tabs(["لوحة التحكم", "حول المشروع"])
    with tab_view_dash:
        render_dashboard()
    with tab_view_about:
        render_about_panel(config)
    render_app_footer(config.ui)
    st.stop()

render_app_header(config.ui)


def _execute_batch_analysis(comments: list[str]) -> None:
    if not comments:
        st.warning("أدخل تعليقاً واحداً على الأقل.")
        return
    try:
        predictor = get_predictor(model_kind)
        with st.spinner(f"جاري تحليل {len(comments)} تعليق..."):
            out_df, results = run_batch_sentiment_analysis(
                comments,
                predictor,
                auto_lang=auto_lang,
                lang_choice=lang_choice,
            )
        st.session_state["batch_results"] = out_df
        st.session_state["batch_raw_results"] = results
        append_batch_to_history(results)
        st.success(f"تم تحليل {len(out_df)} تعليق.")
        render_batch_summary(out_df)
        render_batch_results_table(out_df)
        user = current_user()
        render_batch_analytics(
            out_df,
            results,
            user_id=user["id"] if user else None,
            model_kind=model_kind,
            source=st.session_state.get("batch_source", "manual"),
            title=st.session_state.get("batch_title", "Batch Analysis"),
        )
        st.download_button(
            "تصدير النتائج CSV",
            data=out_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="comments_sentiment_results.csv",
            mime="text/csv",
            use_container_width=True,
        )
    except FileNotFoundError as exc:
        st.error(str(exc))

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
    render_dashboard()

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
                        tfidf_result, bert_result, result = predict_both_models(
                            get_predictor,
                            comment,
                            lang,
                            compare_enabled=compare_models,
                            preferred_model=model_kind,
                        )
                    st.session_state["last_result"] = result
                    st.session_state["last_comment"] = comment
                    st.session_state["compare_tfidf"] = tfidf_result
                    st.session_state["compare_bert"] = bert_result
                    append_history(result)
                except FileNotFoundError as exc:
                    st.error(str(exc))
                except ValueError as exc:
                    st.error(str(exc))

    with col_result:
        st.markdown("#### النتيجة")
        last = st.session_state.get("last_result")
        last_comment = st.session_state.get("last_comment", "")

        if last:
            render_sentiment_result(last, rtl=is_arabic(last_comment or last.get("text", "")))
            st.markdown("##### توزيع الاحتمالات")
            render_distribution_pie(last["distribution"])
        else:
            render_empty_result_panel()

    last = st.session_state.get("last_result")
    last_comment = st.session_state.get("last_comment", "")

    if last and last_comment:
        if compare_models and st.session_state.get("compare_tfidf"):
            st.divider()
            render_model_comparison_table(
                st.session_state.get("compare_tfidf"),
                st.session_state.get("compare_bert"),
            )

        st.divider()
        col_wc, col_lime = st.columns(2)
        with col_wc:
            st.markdown("#### سحابة الكلمات")
            render_wordcloud(last["cleaned_text"] or last["text"])
        with col_lime:
            render_lime_explanation(
                get_predictor("tfidf"),
                last_comment,
                language=last["language"],
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
        if st.button("تحميل أمثلة العرض", use_container_width=True):
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
        uploaded = st.file_uploader("CSV (عمود text)", type=["csv"])
        if uploaded is not None:
            try:
                comments = load_comments_from_upload(uploaded)
                st.success(f"تم تحميل {len(comments)} تعليق.")
            except ValueError as exc:
                st.error(str(exc))

    analyze_many = st.button("تحليل المجموعة", type="primary", use_container_width=True)

    if analyze_many:
        st.session_state["batch_source"] = "manual"
        st.session_state["batch_title"] = f"Manual batch ({len(comments)} comments)"
        _execute_batch_analysis(comments)

    elif st.session_state.get("batch_results") is not None:
        out_df = st.session_state["batch_results"]
        render_batch_summary(out_df)
        render_batch_results_table(out_df)

with tab_live:
    render_live_import_panel(
        max_batch_size=MAX_BATCH_SIZE,
        on_analyze=_execute_batch_analysis,
    )


with st.expander("📊 أداء النماذج / Model Metrics"):
    paths = ProjectPaths.from_project_root(get_project_root())
    demo_bert_path = os.path.join(paths.reports_dir, "validation_demo_bert.json")
    demo_tfidf_path = os.path.join(paths.reports_dir, "validation_demo_tfidf.json")
    algo_path = os.path.join(paths.reports_dir, "algorithm_comparison.json")

    st.info("للعرض: استخدم **BERT** (~76% F1) | TF-IDF (~67% F1) + LIME")

    m1, m2, m3 = st.columns(3)
    with m1:
        if os.path.exists(demo_bert_path):
            with open(demo_bert_path, "r", encoding="utf-8") as handle:
                demo_bert = json.load(handle)
            st.metric("BERT — Demo", f"{demo_bert.get('macro_f1', 0):.1%}")
        else:
            st.caption("python evaluate.py --model bert")

    with m2:
        if os.path.exists(demo_tfidf_path):
            with open(demo_tfidf_path, "r", encoding="utf-8") as handle:
                demo_tfidf = json.load(handle)
            st.metric("TF-IDF — Demo", f"{demo_tfidf.get('macro_f1', 0):.1%}")
        elif os.path.exists(algo_path):
            with open(algo_path, "r", encoding="utf-8") as handle:
                algo = json.load(handle)
            winner = algo.get("winner", {})
            st.metric("Best Algorithm", winner.get("algorithm", "—"))
            st.caption(f"Demo F1: {winner.get('validation_macro_f1', 0):.1%}")

    with m3:
        full_bert = os.path.join(paths.reports_dir, "validation_bert.json")
        if os.path.exists(full_bert):
            with open(full_bert, "r", encoding="utf-8") as handle:
                full = json.load(handle)
            st.metric("BERT — Full test", f"{full.get('macro_f1', 0):.1%}")

    if os.path.exists(algo_path):
        with open(algo_path, "r", encoding="utf-8") as handle:
            algo = json.load(handle)
        st.markdown("**Algorithm ranking (Validation F1):**")
        for row in algo.get("ranking", [])[:6]:
            st.write(
                f"• **{row['label']}** ({row['algorithm']}): "
                f"Validation F1 = {row['validation_macro_f1']:.1%} | "
                f"Synthetic CV F1 = {row['cv_f1_macro_synthetic']:.1%}"
            )

    cmp_path = os.path.join(paths.reports_dir, "model_comparison.json")
    if os.path.exists(cmp_path):
        with open(cmp_path, "r", encoding="utf-8") as handle:
            cmp_data = json.load(handle)
        st.markdown("**مقارنة TF-IDF vs BERT:**")
        for row in cmp_data.get("summary", []):
            st.write(
                f"• **{row['model']}** على {row['dataset']}: "
                f"F1 = {row['macro_f1']:.1%} | Accuracy = {row['accuracy']:.1%}"
            )

render_app_footer(config.ui)
