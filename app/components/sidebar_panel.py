"""Sidebar content for the main application."""

from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from components.auth_panel import current_user


def _session_stats(history: List[Dict[str, Any]]) -> Dict[str, int]:
    counts = {"total": len(history), "positive": 0, "negative": 0, "neutral": 0}
    for item in history:
        sentiment = item.get("sentiment", "neutral")
        if sentiment in counts:
            counts[sentiment] += 1
    return counts


def render_session_summary() -> None:
    history: List[Dict[str, Any]] = st.session_state.get("history", [])
    stats = _session_stats(history)

    st.markdown("**ملخص الجلسة**")
    if stats["total"] == 0:
        st.caption("لم تُجرَ تحليلات بعد.")
        return

    c1, c2 = st.columns(2)
    c1.metric("تحليلات", stats["total"])
    avg_conf = sum(float(h.get("confidence", 0)) for h in history) / stats["total"]
    c2.metric("متوسط اليقين", f"{avg_conf:.0f}%")

    p, n, u = stats["positive"], stats["negative"], stats["neutral"]
    st.caption(f"إيجابي {p} · سلبي {n} · محايد {u}")


def render_sidebar_extras(ui_config: Dict[str, Any]) -> tuple[bool, str]:
    st.divider()
    render_session_summary()

    st.divider()
    st.markdown("**اللغة**")
    auto_lang = st.toggle("كشف تلقائي للغة", value=True)
    lang_choice = "ar_shami"
    if not auto_lang:
        lang_choice = st.selectbox(
            "اللغة",
            options=["en", "ar_fusha", "ar_shami"],
            format_func=lambda x: {"en": "English", "ar_fusha": "عربي فصحى", "ar_shami": "عربي شامي"}[x],
            label_visibility="collapsed",
        )
    st.caption("يدعم: عربي · English · شامي")

    st.divider()
    st.markdown("**المظهر**")
    dark_mode = st.toggle(
        "الوضع الداكن",
        value=st.session_state.get("dark_mode", False),
    )
    st.session_state["dark_mode"] = dark_mode

    render_sidebar_account()

    return auto_lang, lang_choice, dark_mode


def render_sidebar_account() -> None:
    user = current_user()
    if not user:
        return

    st.divider()
    if st.button("تسجيل الخروج", key="sidebar_logout", use_container_width=True):
        st.session_state["auth_user"] = None
        st.rerun()
