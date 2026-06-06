"""About page with project links and QR code for demo."""

from __future__ import annotations

import urllib.parse
from typing import Any, Dict

import streamlit as st

from cloud_setup import is_cloud_runtime


def _platform_urls(config: Any) -> tuple[str, str]:
    platform = getattr(config, "platform", {}) or {}
    github = platform.get("github_url", "https://github.com/AbdAlnaserTech/sham-sentiment")
    app_url = platform.get("app_url", "https://sham-sentiment.streamlit.app")
    return github, app_url


def render_about_panel(config: Any) -> None:
    ui = config.ui
    github_url, app_url = _platform_urls(config)

    st.markdown("### حول المشروع")
    st.markdown(
        f"""
        **{ui.get('university_name_ar', 'جامعة الشام')}** — {ui.get('department_ar', 'مشروع تخرج')}

        منصة لتحليل مشاعر التعليقات (إيجابي / سلبي / محايد) بالعربية والإنجليزية
        باستخدام الذكاء الاصطناعي (BERT + TF-IDF).
        """
    )

    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.markdown("#### روابط المشروع")
        st.link_button("GitHub — الكود المصدري", github_url, use_container_width=True)
        st.link_button("التطبيق على الإنترنت", app_url, use_container_width=True)

        st.markdown("#### المطور")
        st.write(
            f"**{ui.get('author_label', 'إعداد وتطوير')}:** "
            f"{ui.get('author_name_ar', '')} ({ui.get('author_name_en', '')})"
        )

        st.markdown("#### الميزات الرئيسية")
        features = [
            "تحليل تعليق واحد أو آلاف التعليقات دفعة واحدة",
            "نماذج BERT و TF-IDF + شرح LIME",
            "لوحة تحكم، تنبيهات، كلمات مفتاحية",
            "تصدير PDF / Excel / CSV",
            "جلب تعليقات من YouTube و Google Play و Reddit",
            "REST API + قاعدة بيانات + صلاحيات مستخدمين",
        ]
        for item in features:
            st.markdown(f"- {item}")

        if is_cloud_runtime():
            st.caption("☁️ أنت تستخدم النسخة السحابية على Streamlit Community Cloud.")

    with col2:
        st.markdown("#### QR — افتح من الجوال")
        qr_api = (
            "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data="
            + urllib.parse.quote(app_url, safe="")
        )
        st.image(qr_api, caption=app_url, use_container_width=True)

    with st.expander("حسابات العرض"):
        st.markdown(
            """
            | الدور | المستخدم | كلمة المرور | الصلاحيات |
            |-------|----------|-------------|-----------|
            | مدير | `admin` | `Admin@2026` | كامل |
            | محلل | `analyst` | `Analyst@2026` | تحليل + لوحة |
            | عرض | `viewer` | `Viewer@2026` | لوحة فقط |
            """
        )

    st.markdown("#### أداء النماذج (مرجع)")
    st.info(
        "**BERT** — F1 ≈ 76% على عيّنة العرض | **TF-IDF** — F1 ≈ 67% + LIME\n\n"
        "الاختبار الكامل (~513 عينة): BERT F1 ≈ 63%"
    )
