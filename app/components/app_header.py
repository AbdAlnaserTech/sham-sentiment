"""
رأس وتذييل التطبيق — الشعار، البanner، والحالات الفارغة.

يُستدعى من:
  - main.py → render_app_header / render_app_footer
  - shared.py → render_sidebar_brand
  - تبويب «تعليق واحد» → render_empty_result_panel
"""

import base64
import os
from typing import Any, Dict, Optional

import streamlit as st

from paths import get_project_root

# ── بلوك 1: مسارات الشعار الاحتياطية ─────────────────────────────────────
LOGO_CANDIDATES = (
    "assets/logo.png",
    "assets/university_logo.png",
    "assets/university_logo.svg",
)


def _resolve_logo_path(ui_config: Dict[str, Any]) -> Optional[str]:
    """
    يبحث عن ملف الشعار — أولاً من YAML ثم من LOGO_CANDIDATES.

    يرجع المسار الكامل إن وُجد، وإلا None.
    """
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
    """
    يقرأ الشعار ويحوّله إلى data URI لاستخدامه داخل HTML.

    يدعم PNG و SVG.
    """
    if not logo_path or not os.path.exists(logo_path):
        return None
    with open(logo_path, "rb") as handle:
        encoded = base64.b64encode(handle.read()).decode("ascii")
    ext = os.path.splitext(logo_path)[1].lower()
    mime = "image/svg+xml" if ext == ".svg" else "image/png"
    return f"data:{mime};base64,{encoded}"


def render_sidebar_brand(ui_config: Optional[Dict[str, Any]] = None) -> None:
    """
    بطاقة العلامة التجارية في الشريط الجانبي.

    تعرض: الشعار (أو حرف بديل) + اسم الجامعة + عنوان المشروع + القسم.
    """
    ui_config = ui_config or {}
    uni_ar = ui_config.get("university_name_ar", "جامعة الشام").strip()
    dept = ui_config.get("department_ar", "قسم الهندسة المعلوماتية")
    logo_path = _resolve_logo_path(ui_config)
    logo_src = _load_logo_base64(logo_path)

    logo_html = (
        f'<img src="{logo_src}" alt="{uni_ar}" class="sidebar-brand-logo" />'
        if logo_src
        else f'<div class="sidebar-brand-fallback">{uni_ar[0] if uni_ar else "ش"}</div>'
    )

    st.markdown(
        f"""
        <div class="sidebar-brand">
            {logo_html}
            <div class="sidebar-brand-text">
                <div class="sidebar-brand-uni">{uni_ar}</div>
                <div class="sidebar-brand-title">تحليل مشاعر التعليقات</div>
                <div class="sidebar-brand-sub">{dept}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_app_header(ui_config: Optional[Dict[str, Any]] = None) -> None:
    """
    بanner رئيسي أعلى الصفحة — شعار + اسم الجامعة + وصف المشروع.
    """
    ui_config = ui_config or {}
    uni_ar = ui_config.get("university_name_ar", "جامعة الشام").strip()
    uni_en = ui_config.get("university_name_en", "Sham University")
    dept = ui_config.get("department_ar", "قسم الهندسة المعلوماتية")
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
                    <p>منصة لتحليل آراء العملاء — عربي · إنجليزي · لهجة شامية</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_result_panel() -> None:
    """لوحة فارغة في عمود النتيجة قبل أول تحليل."""
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
    """تذييل الصفحة — اسم الجامعة والقسم."""
    ui_config = ui_config or {}
    uni_ar = ui_config.get("university_name_ar", "جامعة الشام").strip()
    dept = ui_config.get("department_ar", "قسم الهندسة المعلوماتية")
    st.markdown(
        f"""
        <div class="app-footer">
            {uni_ar} · {dept}<br>
            منصة تحليل آراء العملاء
        </div>
        """,
        unsafe_allow_html=True,
    )
