"""
لوحة تسجيل الدخول والصلاحيات — Streamlit.

يُتحكم في:
  - حالة auth_user في session_state
  - أدوار admin / analyst / viewer
  - نموذج الدخول وقائمة المستخدم في الشريط الجانبي
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import streamlit as st

from db.auth import user_can_admin, user_can_analyze
from db.repository import authenticate, ensure_default_users


def init_auth_state() -> None:
    """
    يهيّئ حالة المصادقة عند أول تحميل.

    - ensure_default_users → إنشاء حسابات افتراضية إن لم تكن موجودة
    - auth_user = None حتى يسجّل المستخدم الدخول
    """
    ensure_default_users()
    if "auth_user" not in st.session_state:
        st.session_state["auth_user"] = None


def current_user() -> Optional[Dict[str, Any]]:
    """يرجع dict المستخدم الحالي أو None إن لم يكن مسجّل الدخول."""
    return st.session_state.get("auth_user")


def is_logged_in() -> bool:
    """True إذا كان auth_user موجوداً في session_state."""
    return current_user() is not None


def can_analyze() -> bool:
    """
    هل يمكن للمستخدم الحالي تشغيل التحليل؟

    viewer → False | analyst/admin → True
    """
    user = current_user()
    return bool(user and user_can_analyze(user["role"]))


def can_admin() -> bool:
    """
    هل يمكن للمستخدم الحالي إدارة البيانات (حذف دفعات)؟

    admin فقط → True
    """
    user = current_user()
    return bool(user and user_can_admin(user["role"]))


# ── بلوك: تسميات الأدوار للعرض العربي ────────────────────────────────────
ROLE_LABELS_AR = {
    "admin": "مدير النظام",
    "analyst": "محلل",
    "viewer": "عرض فقط",
}


def render_login_form() -> bool:
    """
    يعرض نموذج تسجيل الدخول.

    المخرجات:
      True  → المستخدم مصادق (أو كان مسجّلاً مسبقاً)
      False → لم ينجح الدخول بعد — main.py يوقف التطبيق
    """
    init_auth_state()
    if is_logged_in():
        return True

    st.markdown("### تسجيل الدخول")
    st.caption("منصة تحليل آراء العملاء — جامعة الشام")

    with st.form("login_form"):
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        submitted = st.form_submit_button("دخول", type="primary", use_container_width=True)

    if submitted:
        user = authenticate(username, password)
        if user:
            st.session_state["auth_user"] = user
            st.rerun()
        else:
            st.error("بيانات الدخول غير صحيحة.")

    # ── روابط GitHub والتطبيق من YAML (اختياري) ──
    try:
        from cloud_setup import get_public_app_url
        from config import load_config

        cfg = load_config()
        platform = cfg.platform
        github = platform.get("github_url", "")
        app_url = get_public_app_url(platform) or str(platform.get("app_url", "")).strip() or None

        links = []
        if github:
            links.append(f"[GitHub]({github})")
        if app_url:
            links.append(f"[التطبيق]({app_url})")
        if links:
            st.caption(" · ".join(links))
    except Exception:
        pass

    return False


def render_user_menu() -> None:
    """
    قائمة المستخدم في الشريط الجانبي — الاسم، الدور، زر الخروج.

    (غير مستخدمة حالياً في main — الخروج من sidebar_panel)
    """
    user = current_user()
    if not user:
        return
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**{user.get('full_name_ar', user['username'])}**")
    role_ar = ROLE_LABELS_AR.get(user["role"], user["role"])
    st.sidebar.caption(f"الدور: {role_ar}")
    if st.sidebar.button("تسجيل الخروج من الحساب إن أردت", use_container_width=True):
        st.session_state["auth_user"] = None
        st.rerun()
