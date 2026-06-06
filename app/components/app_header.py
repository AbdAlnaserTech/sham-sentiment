import base64
import os
from typing import Any, Dict, Optional

import streamlit as st

from paths import get_project_root

LOGO_CANDIDATES = (
    "assets/logo.png",
    "assets/university_logo.png",
    "assets/university_logo.svg",
)


def _author_info(ui_config: Dict[str, Any]) -> tuple[str, str, str]:
    name_ar = ui_config.get("author_name_ar", "عبد الناصر حسون")
    name_en = ui_config.get("author_name_en", "Abd Al-Nasser Hassoun")
    label = ui_config.get("author_label", "إعداد وتطوير")
    return name_ar, name_en, label


def _resolve_logo_path(ui_config: Dict[str, Any]) -> Optional[str]:
    configured = ui_config.get("logo_path")
    candidates = []
    if configured:
        candidates.append(configured)
    candidates.extend(LOGO_CANDIDATES)
    for path in candidates:
        full_path = path if os.path.isabs(path) else os.path.join(get_project_root(), path)
        if os.path.exists(full_path):
            return full_path
    return None


def _load_logo_base64(logo_path: Optional[str]) -> Optional[str]:
    if not logo_path or not os.path.exists(logo_path):
        return None
    with open(logo_path, "rb") as handle:
        encoded = base64.b64encode(handle.read()).decode("ascii")
    ext = os.path.splitext(logo_path)[1].lower()
    mime = "image/svg+xml" if ext == ".svg" else "image/png"
    return f"data:{mime};base64,{encoded}"


def render_author_badge(ui_config: Optional[Dict[str, Any]] = None, compact: bool = False) -> None:
    ui_config = ui_config or {}
    name_ar, name_en, label = _author_info(ui_config)

    if compact:
        st.markdown(
            f"""
            <div class="author-badge author-badge-compact">
                <div>
                    <div class="author-label">{label}</div>
                    <div class="author-name">{name_ar}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f"""
        <div class="author-badge">
            <div>
                <div class="author-label">{label}</div>
                <div class="author-name">{name_ar}</div>
                <div class="author-name-en">{name_en}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_app_header(ui_config: Optional[Dict[str, Any]] = None) -> None:
    ui_config = ui_config or {}
    uni_ar = ui_config.get("university_name_ar", "جامعة الشام").strip()
    uni_en = ui_config.get("university_name_en", "Sham University")
    dept = ui_config.get("department_ar", "قسم علوم الحاسوب — مشروع تخرج")
    name_ar, name_en, label = _author_info(ui_config)
    logo_path = _resolve_logo_path(ui_config)
    logo_src = _load_logo_base64(logo_path)

    logo_html = (
        f'<img src="{logo_src}" alt="{uni_ar}" class="hero-logo-img" />'
        if logo_src
        else f'<div class="hero-logo-text">{uni_ar[0] if uni_ar else "ش"}</div>'
    )

    st.markdown(
        f"""
        <div class="hero-banner">
            <div class="hero-inner">
                <div class="hero-logo-wrap">{logo_html}</div>
                <div class="hero-content">
                    <div class="hero-uni">{uni_ar}</div>
                    <div class="hero-uni-sub">{uni_en} · {dept}</div>
                    <h1>تحليل مشاعر التعليقات</h1>
                    <p>Multilingual Sentiment Analysis — English · Arabic · Levantine Dialect</p>
                    <div class="hero-meta">
                        <span>{label}: <strong>{name_ar}</strong></span>
                        <span class="hero-meta-sep">|</span>
                        <span>{name_en}</span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_result_panel() -> None:
    st.markdown(
        """
        <div class="empty-state">
            <strong>لا توجد نتائج بعد</strong><br>
            <small>اكتب تعليقاً أو اختر مثالاً جاهزاً ثم اضغط «تحليل التعليق»</small>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_app_footer(ui_config: Optional[Dict[str, Any]] = None) -> None:
    ui_config = ui_config or {}
    uni_ar = ui_config.get("university_name_ar", "جامعة الشام").strip()
    name_ar, name_en, label = _author_info(ui_config)
    st.markdown(
        f"""
        <div class="app-footer">
            {uni_ar} · مشروع تخرج — تحليل المشاعر متعدد اللغات<br>
            <strong>{label}:</strong> {name_ar} ({name_en})
        </div>
        """,
        unsafe_allow_html=True,
    )
