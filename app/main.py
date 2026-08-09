"""
الواجهة الرئيسية — Streamlit.

هذا الملف للتوجيه فقط:
  1) تسجيل الدخول
  2) الشريط الجانبي
  3) استدعاء كل تبويب من app/tabs/
"""

import bootstrap  # noqa: F401

import streamlit as st
from components.app_header import render_app_footer, render_app_header, render_sidebar_brand
from components.auth_panel import can_admin, can_analyze, render_login_form
from components.ui_styles import apply_app_styles
from cloud_setup import cloud_max_batch_size
from shared import init_app, render_sidebar_settings
from tabs.about import render_about_tab
from tabs.batch import render_batch_tab
from tabs.dashboard import render_dashboard_tab
from tabs.live import render_live_tab
from tabs.single import render_single_tab

st.set_page_config(
    page_title="تحليل آراء العملاء | جامعة الشام",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

paths, config = init_app()

# ── تسجيل الدخول ──
if config.platform.get("require_login", True) and not render_login_form():
    with st.sidebar:
        render_sidebar_brand(config.ui)
    render_app_footer(config.ui)
    st.stop()

auto_lang, lang_choice, _model_kind, rtl_mode, dark_mode = render_sidebar_settings(config.ui)
apply_app_styles(rtl_mode, dark_mode)
max_batch_size = cloud_max_batch_size(int(config.inference.get("max_batch_size", 2000)))

# ── viewer: تبويبان فقط ──
if not can_analyze():
    render_app_header(config.ui)
    st.info("حساب **viewer** — لوحة التحكم و«حول المشروع» فقط (بدون تحليل).")
    tab_dash, tab_about = st.tabs(["لوحة التحكم", "حول المشروع"])
    with tab_dash:
        render_dashboard_tab(can_manage_data=can_admin())
    with tab_about:
        render_about_tab(config)
    render_app_footer(config.ui)
    st.stop()

render_app_header(config.ui)

# ── 5 تبويبات — كل واحد بملف في app/tabs/ ──
tab_dashboard, tab_single, tab_batch, tab_live, tab_about = st.tabs([
    "لوحة التحكم",
    "تعليق واحد",
    "مجموعة تعليقات",
    "جلب من الإنترنت",
    "حول المشروع",
])

with tab_dashboard:
    render_dashboard_tab(can_manage_data=can_admin())

with tab_single:
    render_single_tab(auto_lang=auto_lang, lang_choice=lang_choice)

with tab_batch:
    render_batch_tab(max_batch_size=max_batch_size, auto_lang=auto_lang, lang_choice=lang_choice)

with tab_live:
    render_live_tab(max_batch_size=max_batch_size, auto_lang=auto_lang, lang_choice=lang_choice)

with tab_about:
    render_about_tab(config)

render_app_footer(config.ui)
