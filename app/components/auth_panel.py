"""Simple login panel for Streamlit."""

from __future__ import annotations

from typing import Any, Dict, Optional

import streamlit as st

from db.auth import user_can_admin, user_can_analyze
from db.repository import authenticate, ensure_default_users


def init_auth_state() -> None:
    ensure_default_users()
    if "auth_user" not in st.session_state:
        st.session_state["auth_user"] = None


def current_user() -> Optional[Dict[str, Any]]:
    return st.session_state.get("auth_user")


def is_logged_in() -> bool:
    return current_user() is not None


def can_analyze() -> bool:
    user = current_user()
    return bool(user and user_can_analyze(user["role"]))


def can_admin() -> bool:
    user = current_user()
    return bool(user and user_can_admin(user["role"]))


def render_login_form() -> bool:
    """Return True when user is authenticated."""
    init_auth_state()
    if is_logged_in():
        return True

    st.markdown("### تسجيل الدخول")
    st.caption("منصة تحليل المشاعr — جامعة الشام")

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

    with st.expander("حسابات العرض (Demo)"):
        st.markdown(
            """
            | الدور | المستخدم | كلمة المرور |
            |-------|----------|-------------|
            | مدير | `admin` | `Admin@2026` |
            | محلل | `analyst` | `Analyst@2026` |
            """
        )
    return False


def render_user_menu() -> None:
    user = current_user()
    if not user:
        return
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**{user.get('full_name_ar', user['username'])}**")
    st.sidebar.caption(f"الدور: {user['role']}")
    if st.sidebar.button("تسجيل الخروج", use_container_width=True):
        st.session_state["auth_user"] = None
        st.rerun()
